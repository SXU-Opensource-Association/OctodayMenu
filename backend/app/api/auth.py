from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, password_needs_rehash, verify_password
from app.models import User, UserRole
from app.schemas import (
    AuthResponse,
    AdminMfaChallengeResponse,
    EmailVerificationRequest,
    EmailVerificationResponse,
    LoginRequest,
    UserBase,
    UserCreate,
)
from app.services.login_rate_limit import (
    LoginRateLimitError,
    enforce_login_limit,
    login_key,
    record_login_failure,
    reset_login_failures,
)
from app.services.email import EmailConfigurationError, EmailDeliveryError
from app.services.email_verification import (
    EmailRateLimitError,
    consume_email_code,
    send_email_code,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def build_auth_response(user: User, response: Response) -> AuthResponse:
    settings = get_settings()
    token = create_access_token(subject=user.id, role=user.role.value, session_version=user.session_version)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )
    return AuthResponse(access_token=token, user=user)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册")
    consume_email_code(db, payload.email, payload.verification_code)
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return build_auth_response(user, response)


@router.post(
    "/email-verifications",
    response_model=EmailVerificationResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_email_verification(payload: EmailVerificationRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="邮箱已注册")
    try:
        dev_code = send_email_code(db, payload.email)
    except EmailRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    except (EmailConfigurationError, EmailDeliveryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="邮件服务暂不可用",
        ) from exc
    return EmailVerificationResponse(dev_code=dev_code)


@router.post("/login", response_model=AuthResponse | AdminMfaChallengeResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    key = login_key(payload.email, request.client.host if request.client else None)
    try:
        enforce_login_limit(key)
    except LoginRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        record_login_failure(key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已停用")
    if user.is_blacklisted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被列入黑名单")
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
        db.commit()
    if user.role in {UserRole.ADMIN, UserRole.SUPER_ADMIN}:
        if payload.verification_code is None:
            reset_login_failures(key)
            try:
                dev_code = send_email_code(db, user.email, purpose="管理员登录")
            except EmailRateLimitError as exc:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=str(exc),
                    headers={"Retry-After": str(exc.retry_after_seconds)},
                ) from exc
            except (EmailConfigurationError, EmailDeliveryError) as exc:
                raise HTTPException(status_code=503, detail="邮件服务暂不可用") from exc
            response.status_code = status.HTTP_202_ACCEPTED
            return AdminMfaChallengeResponse(dev_code=dev_code)
        try:
            consume_email_code(db, user.email, payload.verification_code)
        except HTTPException:
            record_login_failure(key)
            raise
    reset_login_failures(key)
    return build_auth_response(user, response)


@router.get("/me", response_model=UserBase)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    current_user.session_version += 1
    db.commit()
    response.delete_cookie(settings.auth_cookie_name, path="/", samesite="lax")
    return {"status": "ok"}
