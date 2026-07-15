import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


async def save_resume_file(file: UploadFile, user_id: int) -> tuple[str, int, str, str]:
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="仅支持 PDF、DOC 和 DOCX 简历")
    data = await file.read(settings.max_upload_bytes + 1)
    if not data:
        raise HTTPException(status_code=422, detail="简历文件不能为空")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="简历文件不能超过 10MB")

    relative = Path(str(user_id)) / f"{uuid4().hex}{ALLOWED_TYPES[content_type]}"
    target = Path(settings.upload_dir) / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return relative.as_posix(), len(data), hashlib.sha256(data).hexdigest(), content_type


def delete_resume_file(storage_key: str) -> None:
    target = (Path(settings.upload_dir) / storage_key).resolve()
    root = Path(settings.upload_dir).resolve()
    if root in target.parents and target.exists():
        target.unlink()
