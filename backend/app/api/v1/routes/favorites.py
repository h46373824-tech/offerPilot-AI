import math

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, Db
from app.models import Favorite, Job
from app.schemas import FavoriteCreate, FavoriteOut, Page

router = APIRouter(prefix="/favorites", tags=["收藏"])


@router.get("", response_model=Page[FavoriteOut])
def list_favorites(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[FavoriteOut]:
    filters = [Favorite.user_id == user.id]
    total = db.scalar(select(func.count(Favorite.id)).where(*filters)) or 0
    stmt = (
        select(Favorite)
        .where(*filters)
        .order_by(Favorite.created_at.desc())
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


@router.post("", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(payload: FavoriteCreate, db: Db, user: CurrentUser) -> Favorite:
    if db.get(Job, payload.job_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="岗位不存在")
    existing = db.scalar(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.job_id == payload.job_id)
    )
    if existing is not None:
        return existing

    item = Favorite(user_id=user.id, job_id=payload.job_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(job_id: int, db: Db, user: CurrentUser) -> None:
    item = db.scalar(select(Favorite).where(Favorite.user_id == user.id, Favorite.job_id == job_id))
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏不存在")
    db.delete(item)
    db.commit()
