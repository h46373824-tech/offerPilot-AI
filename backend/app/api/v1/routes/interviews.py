import math
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentUser, Db
from app.api.v1.routes.applications import get_user_application
from app.models import Interview
from app.schemas import InterviewCreate, InterviewOut, InterviewUpdate, Page
from app.services.audit import record_audit

router = APIRouter(prefix="/interviews", tags=["面试记录"])
INTERVIEW_TRANSITIONS = {
    "scheduled": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": {"scheduled"},
}


def _get_interview(db: Db, user_id: int, item_id: int) -> Interview:
    item = db.scalar(select(Interview).where(Interview.id == item_id, Interview.user_id == user_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="面试记录不存在")
    return item


@router.get("", response_model=Page[InterviewOut])
def list_interviews(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    interview_status: str | None = Query(default=None, alias="status"),
    sort_by: Literal["scheduled_at", "created_at", "status"] = "scheduled_at",
    order: Literal["asc", "desc"] = "asc",
) -> Page[InterviewOut]:
    filters: list[ColumnElement[bool]] = [Interview.user_id == user.id]
    if interview_status:
        filters.append(Interview.status == interview_status)

    total = db.scalar(select(func.count(Interview.id)).where(*filters)) or 0
    sort_columns = {
        "scheduled_at": Interview.scheduled_at,
        "created_at": Interview.created_at,
        "status": Interview.status,
    }
    column = sort_columns[sort_by]
    stmt = (
        select(Interview)
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


@router.get("/{item_id}", response_model=InterviewOut)
def get_interview(item_id: int, db: Db, user: CurrentUser) -> Interview:
    return _get_interview(db, user.id, item_id)


@router.post("", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(payload: InterviewCreate, db: Db, user: CurrentUser) -> Interview:
    application = get_user_application(db, user.id, payload.application_id)
    item = Interview(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.flush()
    if application.status in {"applied", "written_test"}:
        application.status = "interview"
    record_audit(
        db,
        user_id=user.id,
        action="interview.created",
        entity_type="interview",
        entity_id=item.id,
        details={"application_id": item.application_id, "scheduled_at": item.scheduled_at},
    )
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=InterviewOut)
def update_interview(
    item_id: int, payload: InterviewUpdate, db: Db, user: CurrentUser
) -> Interview:
    item = _get_interview(db, user.id, item_id)
    changes = payload.model_dump(exclude_unset=True)
    new_status = changes.get("status")
    if (
        new_status is not None
        and new_status != item.status
        and new_status not in INTERVIEW_TRANSITIONS.get(item.status, set())
    ):
        raise HTTPException(status_code=409, detail=f"不能从 {item.status} 流转到 {new_status}")
    previous_status = item.status
    for key, value in changes.items():
        setattr(item, key, value)
    record_audit(
        db,
        user_id=user.id,
        action="interview.updated",
        entity_type="interview",
        entity_id=item.id,
        details={"changes": changes, "previous_status": previous_status},
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(item_id: int, db: Db, user: CurrentUser) -> None:
    item = _get_interview(db, user.id, item_id)
    record_audit(
        db,
        user_id=user.id,
        action="interview.deleted",
        entity_type="interview",
        entity_id=item.id,
        details={"application_id": item.application_id},
    )
    db.delete(item)
    db.commit()
