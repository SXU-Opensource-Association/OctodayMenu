from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_db, require_admin, require_super_admin
from app.core.security import hash_password
from app.models import Announcement, AuditLog, AreaType, Dish, DishTag, FoodArea, FoodSection, FoodVendor, Tag, User, UserRole
from app.schemas import (
    AdminCreate,
    AdminUpdate,
    AnnouncementCreate,
    AnnouncementOut,
    AuditLogOut,
    DishCreate,
    DishOut,
    DishUpdate,
    FloorCreate,
    FloorOut,
    FloorUpdate,
    FoodAreaCreate,
    FoodAreaOut,
    FoodAreaUpdate,
    FoodSectionCreate,
    FoodSectionOut,
    FoodSectionUpdate,
    FoodVendorCreate,
    FoodVendorOut,
    FoodVendorUpdate,
    ImportResult,
    RestaurantCreate,
    RestaurantOut,
    RestaurantUpdate,
    StallCreate,
    StallOut,
    StallUpdate,
    TagCreate,
    TagOut,
    TagUpdate,
    UserBase,
    UserUpdate,
    UploadResponse,
)
from app.services.food_import import build_food_template, import_food_workbook
from app.services.serializers import area_to_dict, dish_to_dict, section_to_dict, vendor_to_dict
from app.services.uploads import read_upload_limited, store_image, validate_image_bytes


router = APIRouter(prefix="/admin", tags=["admin"])
MAX_IMPORT_BYTES = 10 * 1024 * 1024
MAX_ADMIN_IMAGE_BYTES = 5 * 1024 * 1024


def apply_updates(instance, payload) -> None:
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "tag_ids":
            continue
        if key == "address":
            setattr(instance, "location", value)
        else:
            setattr(instance, key, value)


def get_or_404(db: Session, model, object_id: int, message: str):
    instance = db.get(model, object_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=message)
    return instance


def area_options():
    return (
        joinedload(FoodArea.sections).joinedload(FoodSection.vendors).joinedload(FoodVendor.dishes),
        joinedload(FoodArea.vendors).joinedload(FoodVendor.dishes),
    )


@router.get("/users", response_model=list[UserBase])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).filter(User.role == UserRole.USER).order_by(User.id).all()


@router.patch("/users/{user_id}", response_model=UserBase)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = get_or_404(db, User, user_id, "用户不存在")
    if user.role != UserRole.USER:
        raise HTTPException(status_code=400, detail="只能修改普通用户")
    apply_updates(user, payload)
    db.commit()
    db.refresh(user)
    return user


def get_regular_user_or_404(db: Session, user_id: int) -> User:
    user = get_or_404(db, User, user_id, "用户不存在")
    if user.role != UserRole.USER:
        raise HTTPException(status_code=400, detail="只能管理普通用户")
    return user


@router.post("/users/{user_id}/blacklist", response_model=UserBase)
def blacklist_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = get_regular_user_or_404(db, user_id)
    if not user.is_blacklisted:
        user.is_blacklisted = True
        user.session_version += 1
        db.commit()
        db.refresh(user)
    return user


@router.delete("/users/{user_id}/blacklist", response_model=UserBase)
def remove_user_from_blacklist(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = get_regular_user_or_404(db, user_id)
    if user.is_blacklisted:
        user.is_blacklisted = False
        db.commit()
        db.refresh(user)
    return user


@router.post("/users/{user_id}/mute", response_model=UserBase)
def mute_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = get_regular_user_or_404(db, user_id)
    user.is_muted = True
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}/mute", response_model=UserBase)
def unmute_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = get_regular_user_or_404(db, user_id)
    user.is_muted = False
    db.commit()
    db.refresh(user)
    return user


@router.get("/admins", response_model=list[UserBase])
def list_admins(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).filter(User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])).order_by(User.id).all()


@router.post("/admins", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def create_admin(payload: AdminCreate, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    if payload.role != UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="只能新增基本管理员；超级管理员请使用转让功能")
    existing = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="邮箱已注册")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/admins/{admin_id}", response_model=UserBase)
def update_admin(
    admin_id: int,
    payload: AdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    admin = get_or_404(db, User, admin_id, "管理员不存在")
    if admin.role == UserRole.USER:
        raise HTTPException(status_code=400, detail="目标不是管理员")
    if admin.id == current_user.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="超级管理员不能停用自己，请先转让权限")
    apply_updates(admin, payload)
    db.commit()
    db.refresh(admin)
    return admin


@router.post("/admins/{admin_id}/transfer-super-admin", response_model=UserBase)
def transfer_super_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    if admin_id == current_user.id:
        raise HTTPException(status_code=400, detail="目标已经是超级管理员")
    target = db.query(User).filter(User.id == admin_id).with_for_update().one_or_none()
    if target is None or target.role != UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="只能转让给基本管理员")
    if not target.is_active:
        raise HTTPException(status_code=400, detail="目标管理员已停用")
    current = db.query(User).filter(User.id == current_user.id).with_for_update().one()
    target.role = UserRole.SUPER_ADMIN
    current.role = UserRole.ADMIN
    db.commit()
    db.refresh(target)
    return target


@router.delete("/admins/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    admin = get_or_404(db, User, admin_id, "管理员不存在")
    if admin.role == UserRole.USER:
        raise HTTPException(status_code=400, detail="目标不是管理员")
    if admin.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="不能删除超级管理员，请先转让权限")
    db.delete(admin)
    db.commit()
    return {"status": "ok"}


@router.post("/food-areas", response_model=FoodAreaOut, status_code=status.HTTP_201_CREATED)
def create_food_area(payload: FoodAreaCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    area = FoodArea(**payload.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area_to_dict(area)


@router.get("/food-areas", response_model=list[FoodAreaOut])
def admin_list_food_areas(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    areas = db.query(FoodArea).options(*area_options()).order_by(FoodArea.area_type, FoodArea.id).all()
    return [area_to_dict(area) for area in areas]


@router.patch("/food-areas/{area_id}", response_model=FoodAreaOut)
def update_food_area(
    area_id: int,
    payload: FoodAreaUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    area = get_or_404(db, FoodArea, area_id, "就餐地点不存在")
    if payload.area_type is not None and payload.area_type != area.area_type:
        if area.area_type == AreaType.CANTEEN and area.sections:
            raise HTTPException(status_code=400, detail="包含楼层的餐厅不能直接修改为其它地点类型")
        if payload.area_type == AreaType.CANTEEN and area.vendors:
            raise HTTPException(status_code=400, detail="包含直属店铺的地点不能直接修改为餐厅")
    apply_updates(area, payload)
    db.commit()
    db.refresh(area)
    return area_to_dict(area)


@router.delete("/food-areas/{area_id}")
def delete_food_area(area_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    area = get_or_404(db, FoodArea, area_id, "就餐地点不存在")
    db.delete(area)
    db.commit()
    return {"status": "ok"}


@router.post("/food-areas/{area_id}/sections", response_model=FoodSectionOut, status_code=status.HTTP_201_CREATED)
def create_food_section(
    area_id: int,
    payload: FoodSectionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    area = get_or_404(db, FoodArea, area_id, "就餐地点不存在")
    if area.area_type != AreaType.CANTEEN:
        raise HTTPException(status_code=400, detail="只有餐厅类型可以添加楼层")
    section = FoodSection(area_id=area_id, **payload.model_dump())
    db.add(section)
    db.commit()
    db.refresh(section)
    return section_to_dict(section)


@router.patch("/sections/{section_id}", response_model=FoodSectionOut)
def update_food_section(
    section_id: int,
    payload: FoodSectionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    section = get_or_404(db, FoodSection, section_id, "楼层不存在")
    apply_updates(section, payload)
    db.commit()
    db.refresh(section)
    return section_to_dict(section)


@router.delete("/sections/{section_id}")
def delete_food_section(section_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    section = get_or_404(db, FoodSection, section_id, "楼层不存在")
    db.delete(section)
    db.commit()
    return {"status": "ok"}


@router.post("/food-areas/{area_id}/vendors", response_model=FoodVendorOut, status_code=status.HTTP_201_CREATED)
def create_direct_vendor(
    area_id: int,
    payload: FoodVendorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    area = get_or_404(db, FoodArea, area_id, "就餐地点不存在")
    if area.area_type == AreaType.CANTEEN:
        raise HTTPException(status_code=400, detail="餐厅窗口必须挂在楼层下")
    vendor = FoodVendor(area_id=area_id, section_id=None, **payload.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor_to_dict(vendor)


@router.post("/sections/{section_id}/vendors", response_model=FoodVendorOut, status_code=status.HTTP_201_CREATED)
def create_section_vendor(
    section_id: int,
    payload: FoodVendorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    section = get_or_404(db, FoodSection, section_id, "楼层不存在")
    vendor = FoodVendor(area_id=section.area_id, section_id=section.id, **payload.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor_to_dict(vendor)


@router.patch("/vendors/{vendor_id}", response_model=FoodVendorOut)
def update_food_vendor(
    vendor_id: int,
    payload: FoodVendorUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    vendor = get_or_404(db, FoodVendor, vendor_id, "店铺不存在")
    apply_updates(vendor, payload)
    db.commit()
    db.refresh(vendor)
    return vendor_to_dict(vendor)


@router.delete("/vendors/{vendor_id}")
def delete_food_vendor(vendor_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    vendor = get_or_404(db, FoodVendor, vendor_id, "店铺不存在")
    db.delete(vendor)
    db.commit()
    return {"status": "ok"}


def assign_tags(db: Session, dish: Dish, tag_ids: list[int]) -> None:
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(status_code=400, detail="菜品标签不存在")
    dish.tag_links = [DishTag(tag=tag) for tag in tags]


@router.post("/vendors/{vendor_id}/dishes", response_model=DishOut, status_code=status.HTTP_201_CREATED)
def create_vendor_dish(
    vendor_id: int,
    payload: DishCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    get_or_404(db, FoodVendor, vendor_id, "店铺不存在")
    data = payload.model_dump(exclude={"tag_ids"})
    dish = Dish(vendor_id=vendor_id, **data)
    assign_tags(db, dish, payload.tag_ids)
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish_to_dict(dish)


@router.patch("/dishes/{dish_id}", response_model=DishOut)
def update_dish(
    dish_id: int,
    payload: DishUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    dish = get_or_404(db, Dish, dish_id, "菜品不存在")
    apply_updates(dish, payload)
    if payload.tag_ids is not None:
        assign_tags(db, dish, payload.tag_ids)
    db.commit()
    db.refresh(dish)
    return dish_to_dict(dish)


@router.delete("/dishes/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    dish = get_or_404(db, Dish, dish_id, "菜品不存在")
    db.delete(dish)
    db.commit()
    return {"status": "ok"}


@router.get("/import/food-template")
def download_food_template(_: User = Depends(require_admin)):
    content = build_food_template()
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="sxu-food-import-template.xlsx"'},
    )


@router.post("/import/food-data", response_model=ImportResult)
async def import_food_data(
    response: Response,
    dry_run: bool = False,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 文件")
    content = await read_upload_limited(file, MAX_IMPORT_BYTES)
    result = import_food_workbook(db, content, dry_run=dry_run)
    if result.error_count:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return result


@router.post("/uploads/images", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_admin_image(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
):
    data = await read_upload_limited(file, MAX_ADMIN_IMAGE_BYTES)
    extension = validate_image_bytes(file.content_type, data)
    return {"image_url": store_image(data, extension, "admin-images")}


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    limit: int = 200,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    safe_limit = max(1, min(limit, 500))
    return db.query(AuditLog).order_by(AuditLog.id.desc()).limit(safe_limit).all()


@router.get("/announcements", response_model=list[AnnouncementOut])
def list_admin_announcements(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Announcement).order_by(Announcement.published_at.desc(), Announcement.id.desc()).all()


@router.post("/announcements", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def publish_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    announcement = Announcement(
        **payload.model_dump(),
        created_by_id=current_user.id,
        created_by_email=current_user.email,
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    announcement = get_or_404(db, Announcement, announcement_id, "公告不存在")
    db.delete(announcement)
    db.commit()
    return {"status": "ok"}


@router.post("/restaurants", response_model=RestaurantOut, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    payload: RestaurantCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    area = FoodArea(
        area_type=AreaType.CANTEEN,
        name=payload.name,
        description=payload.description,
        location=payload.address,
        is_active=payload.is_active,
    )
    db.add(area)
    db.commit()
    db.refresh(area)
    return area_to_dict(area)


@router.get("/restaurants", response_model=list[RestaurantOut])
def admin_list_restaurants(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    areas = (
        db.query(FoodArea)
        .options(*area_options())
        .filter(FoodArea.area_type == AreaType.CANTEEN)
        .order_by(FoodArea.id)
        .all()
    )
    return [area_to_dict(area) for area in areas]


@router.patch("/restaurants/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(
    restaurant_id: int,
    payload: RestaurantUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    area = get_or_404(db, FoodArea, restaurant_id, "餐厅不存在")
    if area.area_type != AreaType.CANTEEN:
        raise HTTPException(status_code=400, detail="目标不是餐厅")
    apply_updates(area, payload)
    db.commit()
    db.refresh(area)
    return area_to_dict(area)


@router.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    area = get_or_404(db, FoodArea, restaurant_id, "餐厅不存在")
    db.delete(area)
    db.commit()
    return {"status": "ok"}


@router.post("/restaurants/{restaurant_id}/floors", response_model=FloorOut, status_code=status.HTTP_201_CREATED)
def create_floor(
    restaurant_id: int,
    payload: FloorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return create_food_section(restaurant_id, FoodSectionCreate(**payload.model_dump()), db, _)


@router.patch("/floors/{floor_id}", response_model=FloorOut)
def update_floor(
    floor_id: int,
    payload: FloorUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return update_food_section(floor_id, FoodSectionUpdate(**payload.model_dump(exclude_unset=True)), db, _)


@router.delete("/floors/{floor_id}")
def delete_floor(floor_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return delete_food_section(floor_id, db, _)


@router.post("/floors/{floor_id}/stalls", response_model=StallOut, status_code=status.HTTP_201_CREATED)
def create_stall(
    floor_id: int,
    payload: StallCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return create_section_vendor(floor_id, FoodVendorCreate(**payload.model_dump()), db, _)


@router.patch("/stalls/{stall_id}", response_model=StallOut)
def update_stall(
    stall_id: int,
    payload: StallUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return update_food_vendor(stall_id, FoodVendorUpdate(**payload.model_dump(exclude_unset=True)), db, _)


@router.delete("/stalls/{stall_id}")
def delete_stall(stall_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return delete_food_vendor(stall_id, db, _)


@router.post("/stalls/{stall_id}/dishes", response_model=DishOut, status_code=status.HTTP_201_CREATED)
def create_dish(
    stall_id: int,
    payload: DishCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return create_vendor_dish(stall_id, payload, db, _)


@router.get("/tags", response_model=list[TagOut])
def admin_list_tags(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Tag).order_by(Tag.category, Tag.id).all()


@router.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    tag = Tag(**payload.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.patch("/tags/{tag_id}", response_model=TagOut)
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    tag = get_or_404(db, Tag, tag_id, "标签不存在")
    apply_updates(tag, payload)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    tag = get_or_404(db, Tag, tag_id, "标签不存在")
    db.delete(tag)
    db.commit()
    return {"status": "ok"}
