import csv
import io
from datetime import date, datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Company, DataSource, ImportBatch, Job
from app.schemas import CompanyCreate, JobCreate

HEADER_ALIASES = {
    "企业名称": "name",
    "行业": "industry",
    "企业性质": "company_type",
    "官网": "website",
    "校招官网": "campus_website",
    "学历要求": "education_requirement",
    "专科可投": "accepts_college",
    "本科可投": "accepts_bachelor",
    "专业要求": "major_requirement",
    "工作城市": "work_cities",
    "岗位名称": "title",
    "企业": "company_name",
    "岗位类别": "category",
    "岗位描述": "description",
    "任职要求": "requirements",
    "投递链接": "application_url",
    "发布时间": "published_at",
    "截止时间": "deadline",
}


def _clean_row(row: dict[str, str | None]) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    for raw_key, raw_value in row.items():
        key = HEADER_ALIASES.get((raw_key or "").strip(), (raw_key or "").strip())
        if key:
            cleaned[key] = (raw_value or "").strip()
    return cleaned


def _boolean(value: str, default: bool) -> bool:
    if not value:
        return default
    normalized = value.lower()
    if normalized in {"1", "true", "yes", "y", "是"}:
        return True
    if normalized in {"0", "false", "no", "n", "否"}:
        return False
    raise ValueError(f"无法识别布尔值：{value}")


def _date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def _datetime(value: str) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _optional(value: str) -> str | None:
    return value or None


def _company_payload(row: dict[str, str]) -> CompanyCreate:
    return CompanyCreate(
        name=row.get("name", ""),
        industry=row.get("industry", ""),
        company_type=row.get("company_type", ""),
        website=_optional(row.get("website", "")),
        campus_website=_optional(row.get("campus_website", "")),
        logo_url=_optional(row.get("logo_url", "")),
        recruitment_status="unverified",
        open_date=_date(row.get("open_date", "")),
        deadline=_date(row.get("deadline", "")),
        education_requirement=row.get("education_requirement", ""),
        accepts_college=_boolean(row.get("accepts_college", ""), False),
        accepts_bachelor=_boolean(row.get("accepts_bachelor", ""), True),
        major_requirement=_optional(row.get("major_requirement", "")),
        work_cities=row.get("work_cities", ""),
        data_source="import",
        last_verified_at=None,
        is_demo=False,
    )


def _job_payload(row: dict[str, str], company_id: int) -> JobCreate:
    return JobCreate(
        title=row.get("title", ""),
        company_id=company_id,
        category=row.get("category", ""),
        work_cities=row.get("work_cities", ""),
        education_requirement=row.get("education_requirement", ""),
        major_requirement=_optional(row.get("major_requirement", "")),
        description=row.get("description", ""),
        requirements=row.get("requirements", ""),
        application_url=_optional(row.get("application_url", "")),
        published_at=_datetime(row.get("published_at", "")),
        deadline=_datetime(row.get("deadline", "")),
        recruitment_status="unverified",
        data_source="import",
        last_verified_at=None,
        is_demo=False,
    )


def _upsert_company(db: Session, row: dict[str, str], source: DataSource) -> bool:
    payload = _company_payload(row)
    item = db.scalar(
        select(Company).where(
            func.lower(Company.name) == payload.name.lower(), Company.is_demo.is_(False)
        )
    )
    values = payload.model_dump()
    values.update(data_source=source.name, data_source_id=source.id)
    if item is None:
        db.add(Company(**values))
        return True
    for key, value in values.items():
        setattr(item, key, value)
    return False


def _upsert_job(db: Session, row: dict[str, str], source: DataSource) -> bool:
    company_name = row.get("company_name", "")
    if not company_name:
        raise ValueError("缺少 company_name/企业")
    company = db.scalar(
        select(Company).where(
            func.lower(Company.name) == company_name.lower(), Company.is_demo.is_(False)
        )
    )
    if company is None:
        raise ValueError(f"关联企业不存在：{company_name}")
    payload = _job_payload(row, company.id)
    item = db.scalar(
        select(Job).where(
            func.lower(Job.title) == payload.title.lower(),
            Job.company_id == company.id,
            Job.is_demo.is_(False),
        )
    )
    values = payload.model_dump()
    values.update(data_source=source.name, data_source_id=source.id)
    if item is None:
        db.add(Job(**values))
        return True
    for key, value in values.items():
        setattr(item, key, value)
    return False


def import_csv(
    db: Session,
    *,
    source: DataSource,
    uploaded_by: int,
    entity_type: str,
    filename: str,
    content: bytes,
) -> ImportBatch:
    batch = ImportBatch(
        source_id=source.id,
        uploaded_by=uploaded_by,
        entity_type=entity_type,
        filename=filename,
        total_rows=0,
        created_rows=0,
        updated_rows=0,
        skipped_rows=0,
        error_rows=0,
        errors=[],
    )
    db.add(batch)
    errors: list[dict[str, Any]] = []
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        batch.status = "failed"
        batch.error_rows = 1
        batch.errors = [{"row": 0, "message": "CSV 必须使用 UTF-8 编码"}]
        db.commit()
        db.refresh(batch)
        return batch

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        batch.status = "failed"
        batch.error_rows = 1
        batch.errors = [{"row": 0, "message": "CSV 缺少表头"}]
        db.commit()
        db.refresh(batch)
        return batch

    for row_number, raw_row in enumerate(reader, start=2):
        batch.total_rows += 1
        row = _clean_row(raw_row)
        try:
            created = (
                _upsert_company(db, row, source)
                if entity_type == "company"
                else _upsert_job(db, row, source)
            )
            if created:
                batch.created_rows += 1
            else:
                batch.updated_rows += 1
        except (ValueError, ValidationError) as exc:
            batch.error_rows += 1
            if len(errors) < 100:
                errors.append({"row": row_number, "message": str(exc)[:500]})

    batch.errors = errors
    batch.status = "completed_with_errors" if batch.error_rows else "completed"
    source.last_import_at = datetime.now().astimezone()
    db.commit()
    db.refresh(batch)
    return batch
