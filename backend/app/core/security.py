from __future__ import annotations

from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import secrets

from fastapi import HTTPException, status

from app.core.config import get_settings


PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != PASSWORD_ALGORITHM:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(digest, expected)


def password_needs_rehash(password_hash: str) -> bool:
    try:
        algorithm, iterations, _, _ = password_hash.split("$", 3)
        return algorithm != PASSWORD_ALGORITHM or int(iterations) < PASSWORD_ITERATIONS
    except (TypeError, ValueError):
        return True


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(subject: int, role: str, session_version: int = 0) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(subject),
        "role": role,
        "ver": session_version,
        "exp": int(expires_at.timestamp()),
    }
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, str]:
    settings = get_settings()
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录凭证") from exc

    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64encode(expected_signature), encoded_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录凭证")

    try:
        payload = json.loads(_b64decode(encoded_payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效登录凭证") from exc

    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期")
    return payload
