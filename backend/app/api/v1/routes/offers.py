import math
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentUser, Db
from app.api.v1.routes.applications import get_user_application
from app.models import Offer
from app.schemas import OfferCreate, OfferOut, OfferUpdate, Page
from app.services.audit import record_audit

router = APIRouter(prefix="/offers", tags=["Offer 管理"])
OFFER_TRANSITIONS = {
    "pending": {"accepted", "declined", "expired"},
    "accepted": set(),
    "declined": set(),
    "expired": set(),
}


def _get_offer(db: Db, user_id: int, item_id: int) -> Offer:
    item = db.scalar(select(Offer).where(Offer.id == item_id, Offer.user_id == user_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer 记录不存在")
    return item


@router.get("", response_model=Page[OfferOut])
def list_offers(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    offer_status: str | None = Query(default=None, alias="status"),
    sort_by: Literal["created_at", "received_at", "response_deadline"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[OfferOut]:
    filters: list[ColumnElement[bool]] = [Offer.user_id == user.id]
    if offer_status:
        filters.append(Offer.status == offer_status)

    total = db.scalar(select(func.count(Offer.id)).where(*filters)) or 0
    sort_columns = {
        "created_at": Offer.created_at,
        "received_at": Offer.received_at,
        "response_deadline": Offer.response_deadline,
    }
    column = sort_columns[sort_by]
    stmt = (
        select(Offer)
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


@router.get("/{item_id}", response_model=OfferOut)
def get_offer(item_id: int, db: Db, user: CurrentUser) -> Offer:
    return _get_offer(db, user.id, item_id)


@router.post("", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def create_offer(payload: OfferCreate, db: Db, user: CurrentUser) -> Offer:
    application = get_user_application(db, user.id, payload.application_id)
    item = Offer(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.flush()
    if application.status == "interview":
        application.status = "offer"
    record_audit(
        db,
        user_id=user.id,
        action="offer.created",
        entity_type="offer",
        entity_id=item.id,
        details={"application_id": item.application_id, "status": item.status},
    )
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=OfferOut)
def update_offer(item_id: int, payload: OfferUpdate, db: Db, user: CurrentUser) -> Offer:
    item = _get_offer(db, user.id, item_id)
    changes = payload.model_dump(exclude_unset=True)
    new_status = changes.get("status")
    if (
        new_status is not None
        and new_status != item.status
        and new_status not in OFFER_TRANSITIONS.get(item.status, set())
    ):
        raise HTTPException(status_code=409, detail=f"不能从 {item.status} 流转到 {new_status}")
    previous_status = item.status
    for key, value in changes.items():
        setattr(item, key, value)
    record_audit(
        db,
        user_id=user.id,
        action="offer.updated",
        entity_type="offer",
        entity_id=item.id,
        details={"changes": changes, "previous_status": previous_status},
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(item_id: int, db: Db, user: CurrentUser) -> None:
    item = _get_offer(db, user.id, item_id)
    record_audit(
        db,
        user_id=user.id,
        action="offer.deleted",
        entity_type="offer",
        entity_id=item.id,
        details={"application_id": item.application_id},
    )
    db.delete(item)
    db.commit()
