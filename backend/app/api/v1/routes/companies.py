import math
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentAdmin, CurrentUser, Db
from app.models import Company
from app.schemas import CompanyCreate, CompanyOut, CompanyUpdate, Page

router = APIRouter(prefix="/companies", tags=["企业"])


@router.get("", response_model=Page[CompanyOut])
def list_companies(
    db: Db,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    industry: str | None = None,
    company_type: str | None = None,
    education: str | None = None,
    recruitment_status: str | None = None,
    accepts_college: bool | None = None,
    accepts_bachelor: bool | None = None,
    is_demo: bool | None = None,
    sort_by: Literal["name", "created_at", "deadline"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[CompanyOut]:
    filters: list[ColumnElement[bool]] = []
    if search:
        filters.append(
            or_(Company.name.ilike(f"%{search}%"), Company.work_cities.ilike(f"%{search}%"))
        )
    if industry:
        filters.append(Company.industry == industry)
    if company_type:
        filters.append(Company.company_type == company_type)
    if education:
        filters.append(Company.education_requirement.ilike(f"%{education}%"))
    if recruitment_status:
        filters.append(Company.recruitment_status == recruitment_status)
    if accepts_college is not None:
        filters.append(Company.accepts_college.is_(accepts_college))
    if accepts_bachelor is not None:
        filters.append(Company.accepts_bachelor.is_(accepts_bachelor))
    if is_demo is not None:
        filters.append(Company.is_demo.is_(is_demo))
    total = db.scalar(select(func.count(Company.id)).where(*filters)) or 0
    column = getattr(Company, sort_by)
    stmt = (
        select(Company)
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


@router.post("", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: Db, _: CurrentAdmin) -> Company:
    item = Company(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _get_company(db: Db, item_id: int) -> Company:
    item = db.get(Company, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="企业不存在")
    return item


@router.get("/{item_id}", response_model=CompanyOut)
def get_company(item_id: int, db: Db, _: CurrentUser) -> Company:
    return _get_company(db, item_id)


@router.patch("/{item_id}", response_model=CompanyOut)
def update_company(item_id: int, payload: CompanyUpdate, db: Db, _: CurrentAdmin) -> Company:
    item = _get_company(db, item_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_company(item_id: int, db: Db, _: CurrentAdmin) -> None:
    item = _get_company(db, item_id)
    db.delete(item)
    db.commit()
