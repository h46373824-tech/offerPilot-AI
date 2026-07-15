import math
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentUser, Db
from app.models import Application, Job, Resume
from app.schemas import ApplicationCreate, ApplicationOut, ApplicationUpdate, Page
from app.services.audit import record_audit

router = APIRouter(prefix="/applications", tags=["投递记录"])
APPLICATION_TRANSITIONS = {
    "planned": {"applied", "withdrawn"},
    "applied": {"written_test", "interview", "rejected", "withdrawn"},
    "written_test": {"interview", "rejected", "withdrawn"},
    "interview": {"offer", "rejected", "withdrawn"},
    "offer": {"completed", "withdrawn"},
    "rejected": set(),
    "withdrawn": set(),
    "completed": set(),
}


def _validate_resume(db: Db, user_id: int, resume_id: int | None) -> None:
    if (
        resume_id is not None
        and db.scalar(select(Resume.id).where(Resume.id == resume_id, Resume.user_id == user_id))
        is None
    ):
        raise HTTPException(status_code=404, detail="简历不存在")


def get_user_application(db: Db, user_id: int, item_id: int) -> Application:
    item = db.scalar(
        select(Application).where(Application.id == item_id, Application.user_id == user_id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投递记录不存在")
    return item


@router.get("", response_model=Page[ApplicationOut])
def list_applications(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    application_status: str | None = Query(default=None, alias="status"),
    job_id: int | None = Query(default=None, gt=0),
    sort_by: Literal["created_at", "applied_at", "status"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[ApplicationOut]:
    filters: list[ColumnElement[bool]] = [Application.user_id == user.id]
    if application_status:
        filters.append(Application.status == application_status)
    if job_id is not None:
        filters.append(Application.job_id == job_id)

    total = db.scalar(select(func.count(Application.id)).where(*filters)) or 0
    sort_columns = {
        "created_at": Application.created_at,
        "applied_at": Application.applied_at,
        "status": Application.status,
    }
    column = sort_columns[sort_by]
    stmt = (
        select(Application)
        .where(*filters)
        .order_by(asc(column) if order == "asc" else desc(column))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return Page(
        items=list(db.scalars(stmt)),
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{item_id}", response_model=ApplicationOut)
def get_application(item_id: int, db: Db, user: CurrentUser) -> Application:
    return get_user_application(db, user.id, item_id)


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Db, user: CurrentUser) -> Application:
    if db.get(Job, payload.job_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="岗位不存在")
    if payload.status not in APPLICATION_TRANSITIONS:
        raise HTTPException(status_code=422, detail="投递状态无效")
    _validate_resume(db, user.id, payload.resume_id)
    item = Application(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.flush()
    record_audit(
        db,
        user_id=user.id,
        action="application.created",
        entity_type="application",
        entity_id=item.id,
        details={"job_id": item.job_id, "status": item.status, "resume_id": item.resume_id},
    )
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ApplicationOut)
def update_application(
    item_id: int, payload: ApplicationUpdate, db: Db, user: CurrentUser
) -> Application:
    item = get_user_application(db, user.id, item_id)
    changes = payload.model_dump(exclude_unset=True)
    if "resume_id" in changes:
        _validate_resume(db, user.id, changes["resume_id"])
    new_status = changes.get("status")
    if new_status is not None and new_status != item.status:
        allowed = APPLICATION_TRANSITIONS.get(item.status, set())
        if new_status not in allowed:
            raise HTTPException(status_code=409, detail=f"不能从 {item.status} 流转到 {new_status}")
    previous_status = item.status
    for key, value in changes.items():
        setattr(item, key, value)
    record_audit(
        db,
        user_id=user.id,
        action="application.updated",
        entity_type="application",
        entity_id=item.id,
        details={"changes": changes, "previous_status": previous_status},
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(item_id: int, db: Db, user: CurrentUser) -> None:
    item = get_user_application(db, user.id, item_id)
    record_audit(
        db,
        user_id=user.id,
        action="application.deleted",
        entity_type="application",
        entity_id=item.id,
        details={"job_id": item.job_id, "status": item.status},
    )
    db.delete(item)
    db.commit()
