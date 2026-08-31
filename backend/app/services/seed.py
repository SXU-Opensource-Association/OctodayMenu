from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import User, UserRole


def ensure_super_admin(db: Session) -> User | None:
    settings = get_settings()
    if not settings.super_admin_email or not settings.super_admin_password:
        return None

    existing_super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN).order_by(User.id).first()
    if existing_super_admin is not None:
        return existing_super_admin

    email = settings.super_admin_email.strip().lower()
    user = db.query(User).filter(User.email == email).one_or_none()
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(settings.super_admin_password),
            display_name="终极管理员",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
        )
        db.add(user)
    else:
        user.password_hash = hash_password(settings.super_admin_password)
        user.role = UserRole.SUPER_ADMIN
        user.is_active = True
    db.commit()
    db.refresh(user)
    return user
