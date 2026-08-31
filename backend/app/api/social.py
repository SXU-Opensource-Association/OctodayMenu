from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, require_not_muted
from app.models import Comment, CommentLike, FoodVendor, User, VendorLike
from app.schemas import CommentCreate, CommentOut, LikeToggleResponse, UploadResponse
from app.services.serializers import comment_to_dict
from app.services.uploads import read_upload_limited, store_image, validate_image_bytes


router = APIRouter(tags=["social"])

MAX_COMMENT_IMAGE_BYTES = 1024 * 1024


def get_vendor_or_404(db: Session, vendor_id: int) -> FoodVendor:
    vendor = db.get(FoodVendor, vendor_id)
    if vendor is None or not vendor.is_active:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return vendor


@router.post("/vendors/{vendor_id}/like", response_model=LikeToggleResponse)
def toggle_vendor_like(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vendor = get_vendor_or_404(db, vendor_id)
    existing = db.query(VendorLike).filter_by(vendor_id=vendor.id, user_id=current_user.id).one_or_none()
    if existing is None:
        db.add(VendorLike(vendor_id=vendor.id, user_id=current_user.id))
        vendor.like_count += 1
        liked = True
    else:
        db.delete(existing)
        vendor.like_count = max(0, vendor.like_count - 1)
        liked = False
    db.commit()
    db.refresh(vendor)
    return {"liked": liked, "like_count": vendor.like_count}


@router.get("/vendors/{vendor_id}/comments", response_model=list[CommentOut])
def list_vendor_comments(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_vendor_or_404(db, vendor_id)
    comments = (
        db.query(Comment)
        .options(
            joinedload(Comment.user),
            joinedload(Comment.likes),
            joinedload(Comment.replies).joinedload(Comment.user),
            joinedload(Comment.replies).joinedload(Comment.likes),
        )
        .filter(Comment.vendor_id == vendor_id, Comment.parent_id.is_(None))
        .order_by(Comment.created_at.desc(), Comment.id.desc())
        .all()
    )
    return [comment_to_dict(comment, current_user_id=current_user.id) for comment in comments]


@router.post("/vendors/{vendor_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_vendor_comment(
    vendor_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_not_muted),
):
    vendor = get_vendor_or_404(db, vendor_id)
    comment = Comment(
        vendor_id=vendor.id,
        user_id=current_user.id,
        content=payload.content,
        image_url=payload.image_url,
    )
    vendor.comment_count += 1
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment_to_dict(comment, current_user_id=current_user.id)


@router.post("/comments/{comment_id}/replies", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment_reply(
    comment_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_not_muted),
):
    parent = db.get(Comment, comment_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    vendor = get_vendor_or_404(db, parent.vendor_id)
    reply = Comment(
        vendor_id=parent.vendor_id,
        parent_id=parent.id,
        user_id=current_user.id,
        content=payload.content,
        image_url=payload.image_url,
    )
    parent.reply_count += 1
    vendor.comment_count += 1
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return comment_to_dict(reply, current_user_id=current_user.id)


@router.post("/comments/{comment_id}/like", response_model=LikeToggleResponse)
def toggle_comment_like(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail="评论不存在")
    existing = db.query(CommentLike).filter_by(comment_id=comment.id, user_id=current_user.id).one_or_none()
    if existing is None:
        db.add(CommentLike(comment_id=comment.id, user_id=current_user.id))
        comment.like_count += 1
        liked = True
    else:
        db.delete(existing)
        comment.like_count = max(0, comment.like_count - 1)
        liked = False
    db.commit()
    db.refresh(comment)
    return {"liked": liked, "like_count": comment.like_count}


@router.post("/uploads/comment-images", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_comment_image(
    file: UploadFile = File(...),
    _: User = Depends(require_not_muted),
):
    data = await read_upload_limited(file, MAX_COMMENT_IMAGE_BYTES)
    extension = validate_image_bytes(file.content_type, data)
    return {"image_url": store_image(data, extension, "comment-images")}
