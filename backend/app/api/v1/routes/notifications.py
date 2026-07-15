import math

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentUser, Db
from app.models import Notification
from app.schemas import NotificationOut, Page

router = APIRouter(prefix="/notifications", tags=["通知"])


@router.get("", response_model=Page[NotificationOut])
def list_notifications(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
) -> Page[NotificationOut]:
    filters: list[ColumnElement[bool]] = [Notification.user_id == user.id]
    if unread_only:
        filters.append(Notification.is_read.is_(False))

    total = db.scalar(select(func.count(Notification.id)).where(*filters)) or 0
    stmt = (
        select(Notification)
        .where(*filters)
        .order_by(Notification.created_at.desc())
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


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(db: Db, user: CurrentUser) -> None:
    db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()


@router.patch("/{item_id}/read", response_model=NotificationOut)
def mark_read(item_id: int, db: Db, user: CurrentUser) -> Notification:
    item = db.scalar(
        select(Notification).where(
            Notification.id == item_id,
            Notification.user_id == user.id,
        )
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
    item.is_read = True
    db.commit()
    db.refresh(item)
    return item
