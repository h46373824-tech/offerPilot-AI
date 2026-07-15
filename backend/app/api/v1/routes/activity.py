import math

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUser, Db
from app.models import AuditLog
from app.schemas import AuditLogOut, Page, ReminderRunResult
from app.services.reminders import generate_reminders

router = APIRouter(tags=["活动与提醒"])


@router.get("/audit-logs", response_model=Page[AuditLogOut])
def list_audit_logs(
    db: Db, user: CurrentUser, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)
) -> Page[AuditLogOut]:
    total = db.scalar(select(func.count(AuditLog.id)).where(AuditLog.user_id == user.id)) or 0
    items = list(
        db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
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


@router.post("/reminders/run", response_model=ReminderRunResult)
def run_reminders(db: Db, user: CurrentUser) -> ReminderRunResult:
    return generate_reminders(db, user.id)
