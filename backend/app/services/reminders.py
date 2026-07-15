from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Favorite, Interview, Job, Notification, Offer
from app.schemas import ReminderRunResult


def _notification_exists(
    db: Session, user_id: int, notification_type: str, entity_type: str, entity_id: int
) -> bool:
    return (
        db.scalar(
            select(Notification.id).where(
                Notification.user_id == user_id,
                Notification.notification_type == notification_type,
                Notification.related_entity_type == entity_type,
                Notification.related_entity_id == entity_id,
            )
        )
        is not None
    )


def generate_reminders(db: Session, user_id: int) -> ReminderRunResult:
    now = datetime.now(UTC)
    job_count = interview_count = offer_count = 0

    favorite_jobs = db.execute(
        select(Job)
        .join(Favorite, Favorite.job_id == Job.id)
        .where(
            Favorite.user_id == user_id,
            Job.is_demo.is_(False),
            Job.deadline.is_not(None),
            Job.deadline >= now,
            Job.deadline <= now + timedelta(days=7),
        )
    ).scalars()
    for job in favorite_jobs:
        if not _notification_exists(db, user_id, "job_deadline", "job", job.id):
            db.add(
                Notification(
                    user_id=user_id,
                    title="收藏岗位即将截止",
                    content=f"{job.title} 将在 7 天内截止，请前往官方渠道核验。",
                    notification_type="job_deadline",
                    related_entity_type="job",
                    related_entity_id=job.id,
                    scheduled_for=job.deadline,
                )
            )
            job_count += 1

    interviews = db.scalars(
        select(Interview).where(
            Interview.user_id == user_id,
            Interview.status == "scheduled",
            Interview.scheduled_at >= now,
            Interview.scheduled_at <= now + timedelta(days=2),
        )
    )
    for interview in interviews:
        if not _notification_exists(db, user_id, "interview", "interview", interview.id):
            db.add(
                Notification(
                    user_id=user_id,
                    title="面试即将开始",
                    content=f"{interview.interview_type} 已进入 48 小时提醒窗口。",
                    notification_type="interview",
                    related_entity_type="interview",
                    related_entity_id=interview.id,
                    scheduled_for=interview.scheduled_at,
                )
            )
            interview_count += 1

    offers = db.scalars(
        select(Offer).where(
            Offer.user_id == user_id,
            Offer.status == "pending",
            Offer.response_deadline.is_not(None),
            and_(
                Offer.response_deadline >= date.today(),
                Offer.response_deadline <= date.today() + timedelta(days=3),
            ),
        )
    )
    for offer in offers:
        response_deadline = offer.response_deadline
        if response_deadline is None:
            continue
        if not _notification_exists(db, user_id, "offer_deadline", "offer", offer.id):
            db.add(
                Notification(
                    user_id=user_id,
                    title="Offer 回复期限临近",
                    content="你的 Offer 将在 3 天内到达回复期限。",
                    notification_type="offer_deadline",
                    related_entity_type="offer",
                    related_entity_id=offer.id,
                    scheduled_for=datetime.combine(
                        response_deadline, datetime.min.time(), tzinfo=UTC
                    ),
                )
            )
            offer_count += 1

    db.commit()
    total = job_count + interview_count + offer_count
    return ReminderRunResult(
        created=total,
        job_deadlines=job_count,
        interviews=interview_count,
        offers=offer_count,
    )
