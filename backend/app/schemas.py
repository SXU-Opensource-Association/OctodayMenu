from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import AreaType, TagCategory, UserRole


def normalize_email(value: str) -> str:
    value = value.strip().lower()
    if "@" not in value or "." not in value.split("@")[-1]:
        raise ValueError("邮箱格式不正确")
    return value


class UserBase(BaseModel):
    id: int
    email: str
    display_name: str | None = None
    role: UserRole
    is_active: bool
    is_blacklisted: bool = False
    is_muted: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=80)
    verification_code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)
    verification_code: str | None = Field(default=None, min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserBase


class AdminMfaChallengeResponse(BaseModel):
    mfa_required: Literal[True] = True
    message: str = "管理员验证码已发送"
    dev_code: str | None = None


class EmailVerificationRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class EmailVerificationResponse(BaseModel):
    status: Literal["sent"] = "sent"
    dev_code: str | None = None


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=80)
    is_active: bool | None = None


class AdminCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=80)
    role: UserRole = UserRole.ADMIN

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class AdminUpdate(UserUpdate):
    pass


class AuditLogOut(BaseModel):
    id: int
    actor_id: int | None = None
    actor_email: str
    actor_role: str
    action: str
    resource: str
    status_code: int
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=2000)
    level: Literal["INFO", "IMPORTANT"] = "INFO"
    expires_at: datetime | None = None

    @field_validator("title", "content")
    @classmethod
    def normalize_announcement_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("公告内容不能为空")
        return value


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    level: Literal["INFO", "IMPORTANT"]
    created_by_id: int | None = None
    created_by_email: str
    published_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FoodAreaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    area_type: AreaType
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class FoodAreaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    area_type: AreaType | None = None
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class FoodSectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    level: int = 1
    description: str | None = None
    is_active: bool = True


class FoodSectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    level: int | None = None
    description: str | None = None
    is_active: bool | None = None


class FoodVendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    location_hint: str | None = Field(default=None, max_length=120)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class FoodVendorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    location_hint: str | None = Field(default=None, max_length=120)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class RestaurantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    address: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class FloorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    level: int = 1
    description: str | None = None
    is_active: bool = True


class FloorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    level: int | None = None
    description: str | None = None
    is_active: bool | None = None


class StallCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    location_hint: str | None = Field(default=None, max_length=120)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class StallUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    location_hint: str | None = Field(default=None, max_length=120)
    image_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    category: TagCategory
    is_active: bool = True


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    category: TagCategory | None = None
    is_active: bool | None = None


class DishCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool = True
    tag_ids: list[int] = Field(default_factory=list)


class DishUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    is_available: bool | None = None
    tag_ids: list[int] | None = None


class TagOut(BaseModel):
    id: int
    name: str
    category: TagCategory
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DishOut(BaseModel):
    id: int
    vendor_id: int
    stall_id: int
    name: str
    description: str | None = None
    price: Decimal | None = None
    image_url: str | None = None
    is_available: bool
    like_count: int
    comment_count: int
    tags: list[TagOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class StallOut(BaseModel):
    id: int
    area_id: int
    section_id: int | None = None
    floor_id: int
    name: str
    description: str | None = None
    location_hint: str | None = None
    image_url: str | None = None
    is_active: bool
    like_count: int
    comment_count: int
    liked_by_me: bool = False
    dishes: list[DishOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class FloorOut(BaseModel):
    id: int
    area_id: int
    restaurant_id: int
    name: str
    level: int
    description: str | None = None
    is_active: bool
    stalls: list[StallOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RestaurantOut(BaseModel):
    id: int
    area_type: AreaType = AreaType.CANTEEN
    name: str
    description: str | None = None
    location: str | None = None
    address: str | None = None
    is_active: bool
    floors: list[FloorOut] = Field(default_factory=list)
    sections: list[FloorOut] = Field(default_factory=list)
    vendors: list[StallOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RestaurantSummary(BaseModel):
    id: int
    area_type: AreaType = AreaType.CANTEEN
    name: str
    description: str | None = None
    location: str | None = None
    address: str | None = None
    is_active: bool
    floor_count: int
    section_count: int = 0
    stall_count: int
    vendor_count: int = 0
    dish_count: int


class FoodVendorOut(StallOut):
    pass


class FoodSectionOut(FloorOut):
    vendors: list[FoodVendorOut] = Field(default_factory=list)


class FoodAreaOut(RestaurantOut):
    sections: list[FoodSectionOut] = Field(default_factory=list)
    vendors: list[FoodVendorOut] = Field(default_factory=list)


class FoodAreaSummary(RestaurantSummary):
    pass


class LikeToggleResponse(BaseModel):
    liked: bool
    like_count: int


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    image_url: str | None = Field(default=None, max_length=500)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("评论内容不能为空")
        return value


class CommentOut(BaseModel):
    id: int
    vendor_id: int
    parent_id: int | None = None
    content: str
    image_url: str | None = None
    like_count: int
    reply_count: int
    liked_by_me: bool = False
    author: UserBase
    created_at: datetime
    replies: list["CommentOut"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    image_url: str


class ImportErrorItem(BaseModel):
    row: int
    message: str


class ImportRowResult(BaseModel):
    row: int
    status: Literal["created", "updated", "skipped", "error"]
    message: str


class ImportResult(BaseModel):
    dry_run: bool
    created_count: int
    updated_count: int
    skipped_count: int
    error_count: int
    errors: list[ImportErrorItem] = Field(default_factory=list)
    rows: list[ImportRowResult] = Field(default_factory=list)


class DrawRequest(BaseModel):
    restaurant_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)


class DailyDrawOut(BaseModel):
    id: int
    draw_date: str
    dish: DishOut
    food_area: FoodAreaSummary
    section: FoodSectionOut | None = None
    vendor: FoodVendorOut
    restaurant: RestaurantSummary
    stall: StallOut
