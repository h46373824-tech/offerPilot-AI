import math
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.deps import CurrentUser, Db
from app.models import Job, JobAlert, Notification
from app.schemas import JobAlertCreate, JobAlertOut, JobAlertUpdate, JobOut, Page
from app.services.audit import record_audit

router = APIRouter(prefix="/job-alerts", tags=["岗位订阅"])


def _owned_alert(db: Db, user_id: int, alert_id: int) -> JobAlert:
    item = db.scalar(select(JobAlert).where(JobAlert.id == alert_id, JobAlert.user_id == user_id))
    if item is None:
        raise HTTPException(status_code=404, detail="岗位订阅不存在")
    return item


def _matches_query(alert: JobAlert, *, verified_only: bool = False):  # type: ignore[no-untyped-def]
    criteria = alert.criteria or {}
    filters: list[ColumnElement[bool]] = []
    if title := criteria.get("keyword"):
        filters.append(Job.title.ilike(f"%{title}%"))
    if category := criteria.get("category"):
        filters.append(Job.category == category)
    if city := criteria.get("city"):
        filters.append(Job.work_cities.ilike(f"%{city}%"))
    if education := criteria.get("education"):
        filters.append(Job.education_requirement.ilike(f"%{education}%"))
    if verified_only:
        filters.extend([Job.is_demo.is_(False), Job.recruitment_status == "open"])
    return select(Job).where(*filters).order_by(Job.created_at.desc())


@router.get("", response_model=Page[JobAlertOut])
def list_alerts(
    db: Db,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[JobAlertOut]:
    total = db.scalar(select(func.count(JobAlert.id)).where(JobAlert.user_id == user.id)) or 0
    items = list(
        db.scalars(
            select(JobAlert)
            .where(JobAlert.user_id == user.id)
            .order_by(JobAlert.created_at.desc())
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


@router.post("", response_model=JobAlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(payload: JobAlertCreate, db: Db, user: CurrentUser) -> JobAlert:
    next_run = datetime.now(UTC) + (
        timedelta(days=7) if payload.frequency == "weekly" else timedelta(days=1)
    )
    item = JobAlert(user_id=user.id, next_run_at=next_run, **payload.model_dump())
    db.add(item)
    db.flush()
    record_audit(
        db,
        user_id=user.id,
        action="job_alert.created",
        entity_type="job_alert",
        entity_id=item.id,
        details=payload.model_dump(),
    )
    db.commit()
    db.refresh(item)
    return item


@router.get("/{alert_id}/matches", response_model=Page[JobOut])
def preview_matches(
    alert_id: int, db: Db, user: CurrentUser, page_size: int = Query(20, ge=1, le=100)
) -> Page[JobOut]:
    alert = _owned_alert(db, user.id, alert_id)
    items = list(db.scalars(_matches_query(alert).limit(page_size)))
    return Page(items=items, total=len(items), page=1, page_size=page_size, pages=1 if items else 0)


@router.post("/{alert_id}/run", response_model=dict[str, int])
def run_alert(alert_id: int, db: Db, user: CurrentUser) -> dict[str, int]:
    alert = _owned_alert(db, user.id, alert_id)
    if not alert.is_active:
        raise HTTPException(status_code=409, detail="岗位订阅已停用")
    jobs = list(db.scalars(_matches_query(alert, verified_only=True).limit(50)))
    created = 0
    for job in jobs:
        exists = db.scalar(
            select(Notification.id).where(
                Notification.user_id == user.id,
                Notification.notification_type == "job_alert",
                Notification.related_entity_type == "job",
                Notification.related_entity_id == job.id,
            )
        )
        if exists is None:
            db.add(
                Notification(
                    user_id=user.id,
                    title=f"订阅命中：{job.title}",
                    content="有新的已核验岗位符合你的订阅条件。",
                    notification_type="job_alert",
                    related_entity_type="job",
                    related_entity_id=job.id,
                )
            )
            created += 1
    alert.last_run_at = datetime.now(UTC)
    alert.next_run_at = alert.last_run_at + (
        timedelta(days=7) if alert.frequency == "weekly" else timedelta(days=1)
    )
    db.commit()
    return {"matched": len(jobs), "notifications_created": created}


@router.patch("/{alert_id}", response_model=JobAlertOut)
def update_alert(alert_id: int, payload: JobAlertUpdate, db: Db, user: CurrentUser) -> JobAlert:
    item = _owned_alert(db, user.id, alert_id)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(item, key, value)
    record_audit(
        db,
        user_id=user.id,
        action="job_alert.updated",
        entity_type="job_alert",
        entity_id=item.id,
        details=changes,
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Db, user: CurrentUser) -> None:
    item = _owned_alert(db, user.id, alert_id)
    record_audit(
        db,
        user_id=user.id,
        action="job_alert.deleted",
        entity_type="job_alert",
        entity_id=item.id,
        details={"name": item.name},
    )
    db.delete(item)
    db.commit()
