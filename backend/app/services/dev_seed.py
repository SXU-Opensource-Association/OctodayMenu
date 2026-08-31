from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import AreaType, Dish, DishTag, FoodArea, FoodSection, FoodVendor, Tag, TagCategory


@dataclass(frozen=True)
class DishSeed:
    name: str
    description: str
    price: str
    tags: tuple[tuple[str, TagCategory], ...]


def get_or_create_tag(db: Session, name: str, category: TagCategory) -> Tag:
    tag = db.query(Tag).filter_by(name=name, category=category).one_or_none()
    if tag is None:
        tag = Tag(name=name, category=category)
        db.add(tag)
        db.flush()
    return tag


def get_or_create_area(
    db: Session,
    area_type: AreaType,
    name: str,
    description: str,
    location: str,
) -> FoodArea:
    area = db.query(FoodArea).filter_by(area_type=area_type, name=name).one_or_none()
    if area is None:
        area = FoodArea(
            area_type=area_type,
            name=name,
            description=description,
            location=location,
        )
        db.add(area)
        db.flush()
    return area


def get_or_create_section(
    db: Session,
    area: FoodArea,
    name: str,
    level: int,
    description: str,
) -> FoodSection:
    section = db.query(FoodSection).filter_by(area_id=area.id, level=level).one_or_none()
    if section is None:
        section = FoodSection(
            area_id=area.id,
            name=name,
            level=level,
            description=description,
        )
        db.add(section)
        db.flush()
    return section


def get_or_create_vendor(
    db: Session,
    area: FoodArea,
    section: FoodSection | None,
    name: str,
    description: str,
    location_hint: str,
    image_url: str | None,
) -> FoodVendor:
    query = db.query(FoodVendor).filter(
        FoodVendor.area_id == area.id,
        FoodVendor.name == name,
    )
    query = query.filter(FoodVendor.section_id == section.id) if section else query.filter(FoodVendor.section_id.is_(None))
    vendor = query.one_or_none()
    if vendor is None:
        vendor = FoodVendor(
            area_id=area.id,
            section_id=section.id if section else None,
            name=name,
            description=description,
            location_hint=location_hint,
            image_url=image_url,
        )
        db.add(vendor)
        db.flush()
    return vendor


def add_missing_dishes(db: Session, vendor: FoodVendor, dishes: tuple[DishSeed, ...]) -> None:
    existing_names = {
        name
        for (name,) in db.query(Dish.name).filter(Dish.vendor_id == vendor.id).all()
    }
    for seed in dishes:
        if seed.name in existing_names:
            continue
        dish = Dish(
            vendor_id=vendor.id,
            name=seed.name,
            description=seed.description,
            price=Decimal(seed.price),
            is_available=True,
        )
        dish.tag_links = [
            DishTag(tag=get_or_create_tag(db, tag_name, category))
            for tag_name, category in seed.tags
        ]
        db.add(dish)


def seed_development_data(db: Session) -> None:
    rice = ("米", TagCategory.BASIC)
    noodle = ("面", TagCategory.BASIC)
    bun = ("包子", TagCategory.BASIC)
    porridge = ("粥", TagCategory.BASIC)
    spicy = ("辣", TagCategory.TASTE)
    fresh = ("鲜", TagCategory.TASTE)
    light = ("清淡", TagCategory.TASTE)
    sweet = ("甜", TagCategory.TASTE)
    for tag_name, category in (rice, noodle, bun, porridge, spicy, fresh, light, sweet):
        get_or_create_tag(db, tag_name, category)

    canteen = get_or_create_area(
        db,
        AreaType.CANTEEN,
        "文瀛餐厅",
        "主校区常用餐厅，示例数据可在管理端补充",
        "南区",
    )
    first_floor = get_or_create_section(db, canteen, "一层", 1, "快餐、面食和盖饭")
    second_floor = get_or_create_section(db, canteen, "二层", 2, "早餐和便餐")

    noodle_vendor = get_or_create_vendor(
        db,
        canteen,
        first_floor,
        "山西面馆",
        "刀削面、拌面和汤面",
        "一层东侧",
        "https://images.unsplash.com/photo-1555126634-323283e090fa?auto=format&fit=crop&w=900&q=80",
    )
    add_missing_dishes(
        db,
        noodle_vendor,
        (
            DishSeed("油泼刀削面", "香辣筋道，适合想吃面的中午", "12.50", (noodle, spicy)),
            DishSeed("番茄鸡蛋面", "酸甜开胃，汤汁浓郁", "11.00", (noodle, fresh)),
            DishSeed("清汤牛肉面", "清爽鲜香，牛肉现切", "15.00", (noodle, fresh, light)),
        ),
    )

    rice_vendor = get_or_create_vendor(
        db,
        canteen,
        first_floor,
        "米饭套餐",
        "现炒盖饭和套餐",
        "一层中区",
        None,
    )
    add_missing_dishes(
        db,
        rice_vendor,
        (
            DishSeed("宫保鸡丁盖饭", "微辣下饭，花生香脆", "13.00", (rice, spicy)),
            DishSeed("鱼香肉丝盖饭", "酸甜微辣，配菜丰富", "13.00", (rice, spicy)),
            DishSeed("时蔬鸡腿饭", "荤素搭配，口味清淡", "15.00", (rice, light)),
        ),
    )

    breakfast_vendor = get_or_create_vendor(
        db,
        canteen,
        second_floor,
        "早餐窗口",
        "包子、粥和便携早餐",
        "二层西侧",
        None,
    )
    add_missing_dishes(
        db,
        breakfast_vendor,
        (
            DishSeed("鲜肉包", "现蒸肉包，咸鲜多汁", "2.50", (bun, fresh)),
            DishSeed("小米粥", "温热顺口，适合早餐", "3.00", (porridge, light)),
            DishSeed("豆沙包", "松软香甜", "2.00", (bun, sweet)),
        ),
    )

    snack_street = get_or_create_area(
        db,
        AreaType.SNACK_STREET,
        "许西小吃街",
        "校门外小吃聚集区",
        "南门外",
    )
    dumpling_vendor = get_or_create_vendor(
        db,
        snack_street,
        None,
        "东北饺子馆",
        "饺子和家常小菜",
        "入口左侧",
        "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?auto=format&fit=crop&w=900&q=80",
    )
    add_missing_dishes(
        db,
        dumpling_vendor,
        (
            DishSeed("招牌水饺", "手工现包，鲜香耐吃", "15.00", (noodle, fresh)),
            DishSeed("酸辣汤", "胡椒酸辣，适合搭配主食", "6.00", (porridge, spicy)),
        ),
    )

    custom_area = get_or_create_area(
        db,
        AreaType.CUSTOM_AREA,
        "实验楼旁",
        "实验课间常去的便餐点",
        "主楼西侧",
    )
    cafe_vendor = get_or_create_vendor(
        db,
        custom_area,
        None,
        "咖啡简餐",
        "三明治和饮品",
        "连廊附近",
        None,
    )
    add_missing_dishes(
        db,
        cafe_vendor,
        (DishSeed("鸡肉三明治", "适合早八或课间带走", "11.00", (bun, fresh)),),
    )

    db.commit()
