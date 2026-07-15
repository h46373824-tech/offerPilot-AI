import math
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentAdmin, Db
from app.core.config import settings
from app.models import Company, DataSource, ImportBatch, Job
from app.schemas import (
    DataQualityStats,
    DataSourceCreate,
    DataSourceOut,
    DataSourceUpdate,
    ImportBatchOut,
    Page,
    QualitySourceItem,
    ReviewItem,
    ReviewPayload,
)
from app.services.audit import record_audit
from app.services.data_import import import_csv

router = APIRouter(prefix="/admin", tags=["本地数据治理"])


@router.get("/data-sources", response_model=Page[DataSourceOut])
def list_data_sources(
    db: Db,
    _: CurrentAdmin,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> Page[DataSourceOut]:
    total = db.scalar(select(func.count(DataSource.id))) or 0
    items = list(
        db.scalars(
            select(DataSource)
            .order_by(DataSource.created_at.desc())
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


@router.post("/data-sources", response_model=DataSourceOut, status_code=status.HTTP_201_CREATED)
def create_data_source(payload: DataSourceCreate, db: Db, admin: CurrentAdmin) -> DataSource:
    item = DataSource(**payload.model_dump(), created_by=admin.id)
    db.add(item)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="数据源名称已存在") from None
    record_audit(
        db,
        user_id=admin.id,
        action="data_source.created",
        entity_type="data_source",
        entity_id=item.id,
        details={"name": item.name},
    )
    db.commit()
    db.refresh(item)
    return item


@router.patch("/data-sources/{item_id}", response_model=DataSourceOut)
def update_data_source(
    item_id: int, payload: DataSourceUpdate, db: Db, admin: CurrentAdmin
) -> DataSource:
    item = db.get(DataSource, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(item, key, value)
    record_audit(
        db,
        user_id=admin.id,
        action="data_source.updated",
        entity_type="data_source",
        entity_id=item.id,
        details={"fields": sorted(changes)},
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="数据源名称已存在") from None
    db.refresh(item)
    return item


@router.post("/imports", response_model=ImportBatchOut, status_code=status.HTTP_201_CREATED)
async def upload_import(
    db: Db,
    admin: CurrentAdmin,
    source_id: Annotated[int, Form(gt=0)],
    entity_type: Annotated[Literal["company", "job"], Form()],
    file: Annotated[UploadFile, File()],
) -> ImportBatch:
    source = db.get(DataSource, source_id)
    if source is None or not source.is_active:
        raise HTTPException(status_code=404, detail="可用数据源不存在")
    filename = file.filename or "import.csv"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="仅支持 UTF-8 CSV 文件")
    content = await file.read(settings.max_import_bytes + 1)
    if len(content) > settings.max_import_bytes:
        raise HTTPException(status_code=413, detail="CSV 文件超过本地导入大小限制")
    batch = import_csv(
        db,
        source=source,
        uploaded_by=admin.id,
        entity_type=entity_type,
        filename=filename,
        content=content,
    )
    record_audit(
        db,
        user_id=admin.id,
        action="import.completed",
        entity_type="import_batch",
        entity_id=batch.id,
        details={
            "entity_type": entity_type,
            "created": batch.created_rows,
            "updated": batch.updated_rows,
            "errors": batch.error_rows,
        },
    )
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/imports", response_model=Page[ImportBatchOut])
def list_imports(
    db: Db,
    _: CurrentAdmin,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[ImportBatchOut]:
    total = db.scalar(select(func.count(ImportBatch.id))) or 0
    items = list(
        db.scalars(
            select(ImportBatch)
            .order_by(ImportBatch.created_at.desc())
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


@router.get("/review", response_model=Page[ReviewItem])
def review_queue(
    db: Db,
    _: CurrentAdmin,
    entity_type: Literal["company", "job"] = "company",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[ReviewItem]:
    if entity_type == "company":
        filters = [Company.is_demo.is_(False), Company.last_verified_at.is_(None)]
        total = db.scalar(select(func.count(Company.id)).where(*filters)) or 0
        companies = list(
            db.scalars(
                select(Company)
                .where(*filters)
                .order_by(Company.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        items = [
            ReviewItem(
                entity_type="company",
                id=item.id,
                name=item.name,
                source_name=item.data_source,
                recruitment_status=item.recruitment_status,
                last_verified_at=item.last_verified_at,
                updated_at=item.updated_at,
            )
            for item in companies
        ]
    else:
        filters = [Job.is_demo.is_(False), Job.last_verified_at.is_(None)]
        total = db.scalar(select(func.count(Job.id)).where(*filters)) or 0
        jobs = list(
            db.scalars(
                select(Job)
                .where(*filters)
                .order_by(Job.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        company_ids = {item.company_id for item in jobs}
        company_names = {
            company_id: name
            for company_id, name in db.execute(
                select(Company.id, Company.name).where(Company.id.in_(company_ids))
            ).tuples()
        }
        items = [
            ReviewItem(
                entity_type="job",
                id=item.id,
                name=item.title,
                company_name=company_names.get(item.company_id),
                source_name=item.data_source,
                recruitment_status=item.recruitment_status,
                last_verified_at=item.last_verified_at,
                updated_at=item.updated_at,
            )
            for item in jobs
        ]
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.patch("/review/{entity_type}/{item_id}", response_model=ReviewItem)
def review_item(
    entity_type: Literal["company", "job"],
    item_id: int,
    payload: ReviewPayload,
    db: Db,
    admin: CurrentAdmin,
) -> ReviewItem:
    now = datetime.now(UTC)
    recruitment_status = payload.recruitment_status if payload.action == "approve" else "closed"
    if entity_type == "company":
        company = db.get(Company, item_id)
        if company is None or company.is_demo:
            raise HTTPException(status_code=404, detail="待审核记录不存在")
        company.last_verified_at = now
        company.recruitment_status = recruitment_status
        item_name = company.name
        source_name = company.data_source
        company_name = None
    else:
        job = db.get(Job, item_id)
        if job is None or job.is_demo:
            raise HTTPException(status_code=404, detail="待审核记录不存在")
        job.last_verified_at = now
        job.recruitment_status = recruitment_status
        item_name = job.title
        source_name = job.data_source
        company = db.get(Company, job.company_id)
        company_name = company.name if company else None
    record_audit(
        db,
        user_id=admin.id,
        action=f"{entity_type}.{payload.action}",
        entity_type=entity_type,
        entity_id=item_id,
        details={"recruitment_status": recruitment_status},
    )
    db.commit()
    return ReviewItem(
        entity_type=entity_type,
        id=item_id,
        name=item_name,
        company_name=company_name,
        source_name=source_name,
        recruitment_status=recruitment_status,
        last_verified_at=now,
        updated_at=now,
    )


@router.get("/quality", response_model=DataQualityStats)
def quality_stats(db: Db, _: CurrentAdmin) -> DataQualityStats:
    cutoff = datetime.now(UTC) - timedelta(days=30)
    companies_total = db.scalar(select(func.count(Company.id))) or 0
    jobs_total = db.scalar(select(func.count(Job.id))) or 0
    demo_records = (
        db.scalar(select(func.count(Company.id)).where(Company.is_demo.is_(True))) or 0
    ) + (db.scalar(select(func.count(Job.id)).where(Job.is_demo.is_(True))) or 0)
    verified_records = (
        db.scalar(
            select(func.count(Company.id)).where(
                Company.is_demo.is_(False), Company.last_verified_at.is_not(None)
            )
        )
        or 0
    ) + (
        db.scalar(
            select(func.count(Job.id)).where(
                Job.is_demo.is_(False), Job.last_verified_at.is_not(None)
            )
        )
        or 0
    )
    unverified_records = (
        db.scalar(
            select(func.count(Company.id)).where(
                Company.is_demo.is_(False), Company.last_verified_at.is_(None)
            )
        )
        or 0
    ) + (
        db.scalar(
            select(func.count(Job.id)).where(Job.is_demo.is_(False), Job.last_verified_at.is_(None))
        )
        or 0
    )
    stale_records = (
        db.scalar(
            select(func.count(Company.id)).where(
                Company.is_demo.is_(False), Company.last_verified_at < cutoff
            )
        )
        or 0
    ) + (
        db.scalar(
            select(func.count(Job.id)).where(Job.is_demo.is_(False), Job.last_verified_at < cutoff)
        )
        or 0
    )
    sources = list(db.scalars(select(DataSource).order_by(DataSource.name)))
    coverage = [
        QualitySourceItem(
            source_id=source.id,
            source_name=source.name,
            companies=db.scalar(
                select(func.count(Company.id)).where(Company.data_source_id == source.id)
            )
            or 0,
            jobs=db.scalar(select(func.count(Job.id)).where(Job.data_source_id == source.id)) or 0,
        )
        for source in sources
    ]
    return DataQualityStats(
        companies_total=companies_total,
        jobs_total=jobs_total,
        demo_records=demo_records,
        verified_records=verified_records,
        unverified_records=unverified_records,
        stale_records=stale_records,
        active_sources=db.scalar(
            select(func.count(DataSource.id)).where(DataSource.is_active.is_(True))
        )
        or 0,
        import_batches=db.scalar(select(func.count(ImportBatch.id))) or 0,
        source_coverage=coverage,
    )
