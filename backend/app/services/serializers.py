from __future__ import annotations

from app.models import Comment, DailyDraw, Dish, FoodArea, FoodSection, FoodVendor, Tag, User


def tag_to_dict(tag: Tag) -> dict:
    return {
        "id": tag.id,
        "name": tag.name,
        "category": tag.category.value,
        "is_active": tag.is_active,
    }


def dish_to_dict(dish: Dish) -> dict:
    return {
        "id": dish.id,
        "vendor_id": dish.vendor_id,
        "stall_id": dish.vendor_id,
        "name": dish.name,
        "description": dish.description,
        "price": dish.price,
        "image_url": dish.image_url,
        "is_available": dish.is_available,
        "like_count": dish.like_count,
        "comment_count": dish.comment_count,
        "tags": [tag_to_dict(link.tag) for link in dish.tag_links if link.tag.is_active],
    }


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "role": user.role.value,
        "is_active": user.is_active,
    }


def vendor_to_dict(vendor: FoodVendor, include_dishes: bool = True, current_user_id: int | None = None) -> dict:
    liked_by_me = False
    if current_user_id is not None:
        liked_by_me = any(like.user_id == current_user_id for like in vendor.likes)
    return {
        "id": vendor.id,
        "area_id": vendor.area_id,
        "section_id": vendor.section_id,
        "floor_id": vendor.section_id or 0,
        "name": vendor.name,
        "description": vendor.description,
        "location_hint": vendor.location_hint,
        "image_url": vendor.image_url,
        "is_active": vendor.is_active,
        "like_count": vendor.like_count,
        "comment_count": vendor.comment_count,
        "liked_by_me": liked_by_me,
        "dishes": [dish_to_dict(dish) for dish in vendor.dishes if dish.is_available] if include_dishes else [],
    }


def section_to_dict(section: FoodSection, current_user_id: int | None = None) -> dict:
    vendors = [vendor for vendor in section.vendors if vendor.is_active]
    return {
        "id": section.id,
        "area_id": section.area_id,
        "restaurant_id": section.area_id,
        "name": section.name,
        "level": section.level,
        "description": section.description,
        "is_active": section.is_active,
        "vendors": [vendor_to_dict(vendor, current_user_id=current_user_id) for vendor in vendors],
        "stalls": [vendor_to_dict(vendor, current_user_id=current_user_id) for vendor in vendors],
    }


def area_to_dict(area: FoodArea, current_user_id: int | None = None) -> dict:
    sections = [section for section in area.sections if section.is_active]
    direct_vendors = [vendor for vendor in area.vendors if vendor.is_active and vendor.section_id is None]
    section_dicts = [section_to_dict(section, current_user_id=current_user_id) for section in sections]
    vendor_dicts = [vendor_to_dict(vendor, current_user_id=current_user_id) for vendor in direct_vendors]
    return {
        "id": area.id,
        "area_type": area.area_type.value,
        "name": area.name,
        "description": area.description,
        "location": area.location,
        "address": area.location,
        "is_active": area.is_active,
        "sections": section_dicts,
        "floors": section_dicts,
        "vendors": vendor_dicts,
    }


def area_summary_to_dict(area: FoodArea) -> dict:
    sections = [section for section in area.sections if section.is_active]
    direct_vendors = [vendor for vendor in area.vendors if vendor.is_active and vendor.section_id is None]
    section_vendors = [vendor for section in sections for vendor in section.vendors if vendor.is_active]
    vendors = direct_vendors + section_vendors
    dishes = [dish for vendor in vendors for dish in vendor.dishes if dish.is_available]
    section_count = len(sections)
    vendor_count = len(vendors)
    return {
        "id": area.id,
        "area_type": area.area_type.value,
        "name": area.name,
        "description": area.description,
        "location": area.location,
        "address": area.location,
        "is_active": area.is_active,
        "section_count": section_count,
        "floor_count": section_count,
        "vendor_count": vendor_count,
        "stall_count": vendor_count,
        "dish_count": len(dishes),
    }


def draw_to_dict(draw: DailyDraw) -> dict:
    dish = draw.dish
    vendor = dish.vendor
    area = vendor.area
    section = vendor.section
    area_summary = area_summary_to_dict(area)
    vendor_summary = vendor_to_dict(vendor, include_dishes=False)
    return {
        "id": draw.id,
        "draw_date": draw.draw_date.isoformat(),
        "dish": dish_to_dict(dish),
        "food_area": area_summary,
        "section": section_to_dict(section) if section else None,
        "vendor": vendor_summary,
        "restaurant": area_summary,
        "stall": vendor_summary,
    }


def comment_to_dict(comment: Comment, current_user_id: int | None = None, include_replies: bool = True) -> dict:
    liked_by_me = False
    if current_user_id is not None:
        liked_by_me = any(like.user_id == current_user_id for like in comment.likes)
    replies = [comment_to_dict(reply, current_user_id=current_user_id, include_replies=False) for reply in comment.replies]
    return {
        "id": comment.id,
        "vendor_id": comment.vendor_id,
        "parent_id": comment.parent_id,
        "content": comment.content,
        "image_url": comment.image_url,
        "like_count": comment.like_count,
        "reply_count": comment.reply_count,
        "liked_by_me": liked_by_me,
        "author": user_to_dict(comment.user),
        "created_at": comment.created_at,
        "replies": replies if include_replies else [],
    }


restaurant_to_dict = area_to_dict
restaurant_summary_to_dict = area_summary_to_dict
floor_to_dict = section_to_dict
stall_to_dict = vendor_to_dict
