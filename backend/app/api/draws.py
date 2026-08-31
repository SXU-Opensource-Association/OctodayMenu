from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models import DailyDraw, Dish, FoodArea, FoodVendor, User
from app.schemas import DailyDrawOut, DrawRequest
from app.services.serializers import draw_to_dict


router = APIRouter(prefix="/draws", tags=["draws"])


def candidate_query(db: Session):
    return (
        db.query(Dish)
        .join(Dish.vendor)
        .join(FoodVendor.area)
        .options(
            joinedload(Dish.tag_links).joinedload("*"),
            joinedload(Dish.vendor).joinedload(FoodVendor.area),
            joinedload(Dish.vendor).joinedload(FoodVendor.section),
        )
        .filter(
            Dish.is_available.is_(True),
            FoodVendor.is_active.is_(True),
            FoodArea.is_active.is_(True),
        )
    )


@router.get("/today", response_model=DailyDrawOut)
def get_today_draw(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    draw = (
        db.query(DailyDraw)
        .options(
            joinedload(DailyDraw.dish).joinedload(Dish.tag_links).joinedload("*"),
            joinedload(DailyDraw.dish).joinedload(Dish.vendor).joinedload(FoodVendor.area),
            joinedload(DailyDraw.dish).joinedload(Dish.vendor).joinedload(FoodVendor.section),
        )
        .filter(DailyDraw.user_id == current_user.id, DailyDraw.draw_date == today)
        .one_or_none()
    )
    if draw is None:
        raise HTTPException(status_code=404, detail="今天还没有抽签")
    return draw_to_dict(draw)


@router.post("/today", response_model=DailyDrawOut)
def draw_today(
    payload: DrawRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    existing = (
        db.query(DailyDraw)
        .options(
            joinedload(DailyDraw.dish).joinedload(Dish.tag_links).joinedload("*"),
            joinedload(DailyDraw.dish).joinedload(Dish.vendor).joinedload(FoodVendor.area),
            joinedload(DailyDraw.dish).joinedload(Dish.vendor).joinedload(FoodVendor.section),
        )
        .filter(DailyDraw.user_id == current_user.id, DailyDraw.draw_date == today)
        .one_or_none()
    )
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return draw_to_dict(existing)

    dish = candidate_query(db).order_by(func.random()).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="没有可抽取的菜品")

    draw = DailyDraw(
        user_id=current_user.id,
        dish_id=dish.id,
        draw_date=today,
        filters_json=None,
    )
    db.add(draw)
    db.commit()
    db.refresh(draw)
    response.status_code = status.HTTP_201_CREATED
    return draw_to_dict(draw)
