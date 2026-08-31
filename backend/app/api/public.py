from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_db, get_optional_current_user
from app.models import Announcement, AreaType, Dish, FoodArea, FoodSection, FoodVendor, Tag, User
from app.schemas import AnnouncementOut, DishOut, FoodAreaOut, FoodAreaSummary, RestaurantOut, RestaurantSummary, TagOut
from app.services.serializers import area_summary_to_dict, area_to_dict, dish_to_dict


router = APIRouter(tags=["public"])


@router.get("/announcements", response_model=list[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db)):
    return (
        db.query(Announcement)
        .filter(or_(Announcement.expires_at.is_(None), Announcement.expires_at > func.now()))
        .order_by((Announcement.level == "IMPORTANT").desc(), Announcement.published_at.desc(), Announcement.id.desc())
        .limit(20)
        .all()
    )


def area_options():
    return (
        joinedload(FoodArea.sections)
        .joinedload(FoodSection.vendors)
        .joinedload(FoodVendor.dishes)
        .joinedload(Dish.tag_links)
        .joinedload("*"),
        joinedload(FoodArea.vendors).joinedload(FoodVendor.dishes).joinedload(Dish.tag_links).joinedload("*"),
    )


@router.get("/food-areas", response_model=list[FoodAreaSummary])
def list_food_areas(area_type: AreaType | None = None, db: Session = Depends(get_db)):
    query = (
        db.query(FoodArea)
        .options(*area_options())
        .filter(FoodArea.is_active.is_(True))
        .order_by(FoodArea.area_type, FoodArea.id)
    )
    if area_type is not None:
        query = query.filter(FoodArea.area_type == area_type)
    return [area_summary_to_dict(area) for area in query.all()]


@router.get("/food-areas/{area_id}", response_model=FoodAreaOut)
def get_food_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    area = (
        db.query(FoodArea)
        .options(*area_options())
        .filter(FoodArea.id == area_id, FoodArea.is_active.is_(True))
        .one_or_none()
    )
    if area is None:
        raise HTTPException(status_code=404, detail="就餐地点不存在")
    return area_to_dict(area, current_user_id=current_user.id if current_user else None)


@router.get("/restaurants", response_model=list[RestaurantSummary])
def list_restaurants(db: Session = Depends(get_db)):
    areas = (
        db.query(FoodArea)
        .options(*area_options())
        .filter(FoodArea.is_active.is_(True), FoodArea.area_type == AreaType.CANTEEN)
        .order_by(FoodArea.id)
        .all()
    )
    return [area_summary_to_dict(area) for area in areas]


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    area = (
        db.query(FoodArea)
        .options(*area_options())
        .filter(FoodArea.id == restaurant_id, FoodArea.is_active.is_(True), FoodArea.area_type == AreaType.CANTEEN)
        .one_or_none()
    )
    if area is None:
        raise HTTPException(status_code=404, detail="餐厅不存在")
    return area_to_dict(area)


@router.get("/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).filter(Tag.is_active.is_(True)).order_by(Tag.category, Tag.id).all()


@router.get("/dishes", response_model=list[DishOut])
def list_dishes(
    tag_ids: Annotated[list[int] | None, Query()] = None,
    area_id: int | None = None,
    area_type: AreaType | None = None,
    restaurant_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Dish)
        .join(Dish.vendor)
        .join(FoodVendor.area)
        .options(joinedload(Dish.tag_links).joinedload("*"), joinedload(Dish.vendor).joinedload(FoodVendor.area))
        .filter(
            Dish.is_available.is_(True),
            FoodVendor.is_active.is_(True),
            FoodArea.is_active.is_(True),
        )
        .order_by(Dish.id)
    )
    if restaurant_id is not None:
        area_id = restaurant_id
    if area_id is not None:
        query = query.filter(FoodArea.id == area_id)
    if area_type is not None:
        query = query.filter(FoodArea.area_type == area_type)
    if min_price is not None:
        query = query.filter(Dish.price >= min_price)
    if max_price is not None:
        query = query.filter(Dish.price <= max_price)
    if keyword:
        keyword_like = f"%{keyword.strip()}%"
        query = query.filter(
            Dish.name.ilike(keyword_like)
            | Dish.description.ilike(keyword_like)
            | FoodVendor.name.ilike(keyword_like)
            | FoodVendor.description.ilike(keyword_like)
            | FoodArea.name.ilike(keyword_like)
        )
    for tag_id in tag_ids or []:
        query = query.filter(Dish.tag_links.any(tag_id=tag_id))
    return [dish_to_dict(dish) for dish in query.all()]
