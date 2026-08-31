from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class TagCategory(str, Enum):
    BASIC = "basic"
    TASTE = "taste"


class AreaType(str, Enum):
    CANTEEN = "CANTEEN"
    SNACK_STREET = "SNACK_STREET"
    CUSTOM_AREA = "CUSTOM_AREA"


class EmailDeliveryStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(80))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_muted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    session_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    draws: Mapped[list["DailyDraw"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    vendor_likes: Mapped[list["VendorLike"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comment_likes: Mapped[list["CommentLike"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor")


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    created_by_email: Mapped[str] = mapped_column(String(255), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    created_by: Mapped[User | None] = relationship(foreign_keys=[created_by_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(32), nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    resource: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    actor: Mapped[User | None] = relationship(back_populates="audit_logs")


class FoodArea(TimestampMixin, Base):
    __tablename__ = "food_areas"
    __table_args__ = (UniqueConstraint("area_type", "name", name="uq_food_area_type_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_type: Mapped[AreaType] = mapped_column(SAEnum(AreaType), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sections: Mapped[list["FoodSection"]] = relationship(
        back_populates="area",
        cascade="all, delete-orphan",
        order_by="FoodSection.level",
    )
    vendors: Mapped[list["FoodVendor"]] = relationship(
        back_populates="area",
        cascade="all, delete-orphan",
        order_by="FoodVendor.id",
        foreign_keys="FoodVendor.area_id",
    )


class FoodSection(TimestampMixin, Base):
    __tablename__ = "food_sections"
    __table_args__ = (UniqueConstraint("area_id", "level", name="uq_food_section_area_level"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("food_areas.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    area: Mapped[FoodArea] = relationship(back_populates="sections")
    vendors: Mapped[list["FoodVendor"]] = relationship(
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="FoodVendor.id",
    )


class FoodVendor(TimestampMixin, Base):
    __tablename__ = "food_vendors"
    __table_args__ = (UniqueConstraint("area_id", "section_id", "name", name="uq_food_vendor_area_section_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("food_areas.id", ondelete="CASCADE"), nullable=False)
    section_id: Mapped[int | None] = mapped_column(ForeignKey("food_sections.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location_hint: Mapped[str | None] = mapped_column(String(120))
    image_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    area: Mapped[FoodArea] = relationship(back_populates="vendors", foreign_keys=[area_id])
    section: Mapped[FoodSection | None] = relationship(back_populates="vendors")
    dishes: Mapped[list["Dish"]] = relationship(
        back_populates="vendor",
        cascade="all, delete-orphan",
        order_by="Dish.id",
    )
    likes: Mapped[list["VendorLike"]] = relationship(back_populates="vendor", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="vendor", cascade="all, delete-orphan")


class VendorLike(TimestampMixin, Base):
    __tablename__ = "vendor_likes"
    __table_args__ = (UniqueConstraint("vendor_id", "user_id", name="uq_vendor_like_vendor_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("food_vendors.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    vendor: Mapped[FoodVendor] = relationship(back_populates="likes")
    user: Mapped[User] = relationship(back_populates="vendor_likes")


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", "category", name="uq_tag_name_category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    category: Mapped[TagCategory] = mapped_column(SAEnum(TagCategory), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    dishes: Mapped[list["DishTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan")


class DishTag(Base):
    __tablename__ = "dish_tags"
    __table_args__ = (UniqueConstraint("dish_id", "tag_id", name="uq_dish_tag"),)

    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    dish: Mapped["Dish"] = relationship(back_populates="tag_links")
    tag: Mapped[Tag] = relationship(back_populates="dishes")


class Dish(TimestampMixin, Base):
    __tablename__ = "dishes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("food_vendors.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(500))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    vendor: Mapped[FoodVendor] = relationship(back_populates="dishes")
    tag_links: Mapped[list[DishTag]] = relationship(back_populates="dish", cascade="all, delete-orphan")
    draws: Mapped[list["DailyDraw"]] = relationship(back_populates="dish")


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("food_vendors.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500))
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reply_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    vendor: Mapped[FoodVendor] = relationship(back_populates="comments")
    user: Mapped[User] = relationship(back_populates="comments")
    parent: Mapped["Comment | None"] = relationship(
        back_populates="replies",
        remote_side="Comment.id",
    )
    replies: Mapped[list["Comment"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
        order_by="Comment.created_at",
    )
    likes: Mapped[list["CommentLike"]] = relationship(back_populates="comment", cascade="all, delete-orphan")


class CommentLike(TimestampMixin, Base):
    __tablename__ = "comment_likes"
    __table_args__ = (UniqueConstraint("comment_id", "user_id", name="uq_comment_like_comment_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    comment: Mapped[Comment] = relationship(back_populates="likes")
    user: Mapped[User] = relationship(back_populates="comment_likes")


class DailyDraw(TimestampMixin, Base):
    __tablename__ = "daily_draws"
    __table_args__ = (UniqueConstraint("user_id", "draw_date", name="uq_daily_draw_user_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dish_id: Mapped[int] = mapped_column(ForeignKey("dishes.id"), nullable=False)
    draw_date: Mapped[date] = mapped_column(Date, nullable=False)
    filters_json: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="draws")
    dish: Mapped[Dish] = relationship(back_populates="draws")


class EmailVerification(TimestampMixin, Base):
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivery_status: Mapped[EmailDeliveryStatus] = mapped_column(
        SAEnum(EmailDeliveryStatus),
        default=EmailDeliveryStatus.PENDING,
        nullable=False,
    )
