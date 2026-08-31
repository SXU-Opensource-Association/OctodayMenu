from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.models import EmailDeliveryStatus, EmailVerification
from app.services.email import EmailConfigurationError, EmailDeliveryError, EmailService


VERIFICATION_CODE_TTL = timedelta(minutes=5)
MIN_SEND_INTERVAL = timedelta(minutes=1)
HOURLY_SEND_LIMIT = 5


class EmailRateLimitError(Exception):
    def __init__(self, message: str, retry_after_seconds: int) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


def generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def send_email_code(
    db: Session,
    email: str,
    *,
    now: datetime | None = None,
    email_service: EmailService | None = None,
    purpose: str = "注册",
) -> str | None:
    settings = get_settings()
    current_time = now or datetime.now(timezone.utc)
    _enforce_send_limits(db, email, current_time)

    code = generate_code()
    verification = EmailVerification(
        email=email,
        code_hash=hash_password(code),
        expires_at=current_time + VERIFICATION_CODE_TTL,
        delivery_status=EmailDeliveryStatus.PENDING,
        created_at=current_time,
        updated_at=current_time,
    )
    db.add(verification)
    db.commit()

    if settings.environment == "test":
        verification.delivery_status = EmailDeliveryStatus.SENT
        db.commit()
        return code

    plain_text = f"你的{purpose}验证码是：{code}。验证码 5 分钟内有效，请勿转发给他人。"
    html = f"""
    <div style="font-family:Arial,sans-serif;line-height:1.6;color:#17231d">
      <h2 style="margin:0 0 16px">SXUWhatEat {purpose}验证</h2>
      <p>你的注册验证码是：</p>
      <p style="font-size:28px;font-weight:700;letter-spacing:6px">{code}</p>
      <p>验证码 5 分钟内有效，请勿转发给他人。</p>
    </div>
    """.strip()

    try:
        service = email_service or EmailService(settings)
        service.send_html(
            email,
            f"SXUWhatEat {purpose}验证码",
            html,
            plain_text,
        )
    except (EmailConfigurationError, EmailDeliveryError):
        verification.delivery_status = EmailDeliveryStatus.FAILED
        db.commit()
        raise

    verification.delivery_status = EmailDeliveryStatus.SENT
    db.commit()
    return None


def consume_email_code(db: Session, email: str, code: str) -> None:
    now = datetime.now(timezone.utc)
    verifications = (
        db.query(EmailVerification)
        .filter(
            EmailVerification.email == email,
            EmailVerification.consumed_at.is_(None),
            EmailVerification.delivery_status == EmailDeliveryStatus.SENT,
        )
        .order_by(EmailVerification.id.desc())
        .limit(HOURLY_SEND_LIMIT)
        .all()
    )

    for verification in verifications:
        expires_at = _as_utc(verification.expires_at)
        if expires_at < now:
            continue
        if verify_password(code, verification.code_hash):
            verification.consumed_at = now
            db.commit()
            return

    raise HTTPException(status_code=400, detail="邮箱验证码无效或已过期")


def _enforce_send_limits(db: Session, email: str, now: datetime) -> None:
    attempts = (
        db.query(EmailVerification)
        .filter(EmailVerification.email == email)
        .order_by(EmailVerification.created_at.desc())
        .all()
    )
    if not attempts:
        return

    latest_time = _as_utc(attempts[0].created_at)
    since_latest = now - latest_time
    if since_latest < MIN_SEND_INTERVAL:
        retry_after = max(1, ceil((MIN_SEND_INTERVAL - since_latest).total_seconds()))
        raise EmailRateLimitError("同一邮箱每分钟最多发送一次验证码", retry_after)

    hour_start = now - timedelta(hours=1)
    hourly_attempts = [attempt for attempt in attempts if _as_utc(attempt.created_at) > hour_start]
    if len(hourly_attempts) >= HOURLY_SEND_LIMIT:
        oldest_time = min(_as_utc(attempt.created_at) for attempt in hourly_attempts)
        retry_after = max(1, ceil((oldest_time + timedelta(hours=1) - now).total_seconds()))
        raise EmailRateLimitError("同一邮箱每小时最多发送五次验证码", retry_after)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
