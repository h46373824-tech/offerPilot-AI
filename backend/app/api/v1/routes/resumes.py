import math
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select, update

from app.api.deps import CurrentUser, Db
from app.core.config import settings
from app.models import Application, Resume
from app.schemas import Page, ResumeOut, ResumeUpdate
from app.services.audit import record_audit
from app.services.storage import delete_resume_file, save_resume_file

router = APIRouter(prefix="/resumes", tags=["简历"])


def _owned_resume(db: Db, user_id: int, resume_id: int) -> Resume:
    item = db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))
    if item is None:
        raise HTTPException(status_code=404, detail="简历不存在")
    return item


@router.get("", response_model=Page[ResumeOut])
def list_resumes(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[ResumeOut]:
    total = db.scalar(select(func.count(Resume.id)).where(Resume.user_id == user.id)) or 0
    items = list(
        db.scalars(
            select(Resume)
            .where(Resume.user_id == user.id)
            .order_by(Resume.is_default.desc(), Resume.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    )
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.post("", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    db: Db,
    user: CurrentUser,
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form(min_length=1, max_length=200)],
    version: Annotated[str | None, Form(max_length=50)] = None,
    is_default: Annotated[bool, Form()] = False,
) -> Resume:
    storage_key, file_size, checksum, content_type = await save_resume_file(file, user.id)
    if is_default:
        db.execute(update(Resume).where(Resume.user_id == user.id).values(is_default=False))
    item = Resume(
        user_id=user.id,
        name=name.strip(),
        version=version.strip() if version else None,
        is_default=is_default,
        original_filename=Path(file.filename or "resume.pdf").name,
        content_type=content_type,
        file_size=file_size,
        storage_key=storage_key,
        checksum_sha256=checksum,
        file_url="pending",
    )
    db.add(item)
    db.flush()
    item.file_url = f"/api/v1/resumes/{item.id}/download"
    record_audit(
        db,
        user_id=user.id,
        action="resume.uploaded",
        entity_type="resume",
        entity_id=item.id,
        details={"name": item.name, "version": item.version, "file_size": file_size},
    )
    db.commit()
    db.refresh(item)
    return item


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Db, user: CurrentUser) -> Resume:
    return _owned_resume(db, user.id, resume_id)


@router.get("/{resume_id}/download", response_class=FileResponse)
def download_resume(resume_id: int, db: Db, user: CurrentUser) -> FileResponse:
    item = _owned_resume(db, user.id, resume_id)
    path = (Path(settings.upload_dir) / item.storage_key).resolve()
    if not path.exists():
        raise HTTPException(status_code=404, detail="简历文件不存在")
    return FileResponse(path, media_type=item.content_type, filename=item.original_filename)


@router.patch("/{resume_id}", response_model=ResumeOut)
def update_resume(resume_id: int, payload: ResumeUpdate, db: Db, user: CurrentUser) -> Resume:
    item = _owned_resume(db, user.id, resume_id)
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("is_default") is True:
        db.execute(update(Resume).where(Resume.user_id == user.id).values(is_default=False))
    for key, value in changes.items():
        setattr(item, key, value)
    record_audit(
        db,
        user_id=user.id,
        action="resume.updated",
        entity_type="resume",
        entity_id=item.id,
        details=changes,
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, db: Db, user: CurrentUser) -> None:
    item = _owned_resume(db, user.id, resume_id)
    db.execute(
        update(Application)
        .where(Application.user_id == user.id, Application.resume_id == item.id)
        .values(resume_id=None)
    )
    storage_key = item.storage_key
    record_audit(
        db,
        user_id=user.id,
        action="resume.deleted",
        entity_type="resume",
        entity_id=item.id,
        details={"name": item.name},
    )
    db.delete(item)
    db.commit()
    delete_resume_file(storage_key)
