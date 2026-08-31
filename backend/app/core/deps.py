from collections.abc import Generator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models import User, UserRole


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials if credentials is not None else request.cookies.get("sxuwhateat_auth")
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    payload = decode_access_token(token)
    user_id = int(payload["sub"])
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    if int(payload.get("ver", -1)) != user.session_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录凭证已失效")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已停用")
    if user.is_blacklisted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被列入黑名单")
    request.state.current_user = user
    request.state.audit_actor = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
    }
    return user


def get_optional_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    token = credentials.credentials if credentials is not None else request.cookies.get("sxuwhateat_auth")
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except Exception:
        return None
    user = db.get(User, user_id)
    if (
        user is None
        or int(payload.get("ver", -1)) != user.session_version
        or not user.is_active
        or user.is_blacklisted
    ):
        return None
    request.state.current_user = user
    request.state.audit_actor = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
    }
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限")
    return current_user


def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要终极管理员权限")
    return current_user


def require_not_muted(current_user: User = Depends(get_current_user)) -> User:
    if current_user.is_muted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁言")
    return current_user
