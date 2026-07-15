import math
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentAdmin, CurrentUser, Db
from app.models import Company, Job
from app.schemas import JobCreate, JobOut, JobUpdate, Page

router = APIRouter(prefix="/jobs", tags=["岗位"])


@router.get("", response_model=Page[JobOut])
def list_jobs(
    db: Db,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    city: str | None = None,
    education: str | None = None,
    company_id: int | None = None,
    recruitment_status: str | None = None,
    is_demo: bool | None = None,
    sort_by: Literal["title", "published_at", "deadline", "created_at"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[JobOut]:
    filters: list[ColumnElement[bool]] = []
    if search:
        filters.append(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%"),
                Job.company.has(Company.name.ilike(f"%{search}%")),
            )
        )
    if category:
        filters.append(Job.category == category)
    if city:
        filters.append(Job.work_cities.ilike(f"%{city}%"))
    if education:
        filters.append(Job.education_requirement.ilike(f"%{education}%"))
    if company_id is not None:
        filters.append(Job.company_id == company_id)
    if recruitment_status:
        filters.append(Job.recruitment_status == recruitment_status)
    if is_demo is not None:
        filters.append(Job.is_demo.is_(is_demo))
    total = db.scalar(select(func.count(Job.id)).where(*filters)) or 0
    column = getattr(Job, sort_by)
    stmt = (
        select(Job)
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


def _get(db: Db, item_id: int) -> Job:
    item = db.get(Job, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return item


@router.get("/{item_id}", response_model=JobOut)
def get_job(item_id: int, db: Db, _: CurrentUser) -> Job:
    return _get(db, item_id)


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Db, _: CurrentAdmin) -> Job:
    if db.get(Company, payload.company_id) is None:
        raise HTTPException(status_code=404, detail="企业不存在")
    item = Job(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=JobOut)
def update_job(item_id: int, payload: JobUpdate, db: Db, _: CurrentAdmin) -> Job:
    item = _get(db, item_id)
    changes = payload.model_dump(exclude_unset=True)
    company_id = changes.get("company_id")
    if company_id is not None and db.get(Company, company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="企业不存在")
    for key, value in changes.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_job(item_id: int, db: Db, _: CurrentAdmin) -> None:
    item = _get(db, item_id)
    db.delete(item)
    db.commit()
