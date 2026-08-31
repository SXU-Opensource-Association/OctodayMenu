from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


async def read_upload_limited(file: UploadFile, max_bytes: int) -> bytes:
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件不能超过 {max_bytes // (1024 * 1024)}MB",
        )
    return data


def validate_image_bytes(content_type: str | None, data: bytes) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(content_type or "")
    if extension is None:
        raise HTTPException(status_code=400, detail="只支持 JPEG、PNG 或 WebP 图片")
    if extension == ".jpg" and not data.startswith(b"\xff\xd8"):
        raise HTTPException(status_code=400, detail="图片内容与格式不匹配")
    if extension == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(status_code=400, detail="图片内容与格式不匹配")
    if extension == ".webp" and not (data.startswith(b"RIFF") and data[8:12] == b"WEBP"):
        raise HTTPException(status_code=400, detail="图片内容与格式不匹配")
    return extension


def store_image(data: bytes, extension: str, folder: str) -> str:
    target_dir = BACKEND_ROOT / "uploads" / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (target_dir / filename).write_bytes(data)
    return f"/uploads/{folder}/{filename}"
