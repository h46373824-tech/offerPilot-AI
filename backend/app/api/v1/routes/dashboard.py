from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, Db
from app.models import Application, Company, Interview, Job, Offer
from app.schemas import (
    ApplicationTrendPoint,
    DashboardStats,
    IndustryDistributionItem,
    RecentApplication,
)

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


@router.get("/stats", response_model=DashboardStats)
def stats(db: Db, user: CurrentUser) -> DashboardStats:
    now = datetime.now(UTC)
    soon = now + timedelta(days=14)
    open_company_filters = (
        Company.recruitment_status == "open",
        Company.is_demo.is_(False),
    )
    open_job_filters = (
        Job.recruitment_status == "open",
        Job.is_demo.is_(False),
    )

    company_total = db.scalar(select(func.count(Company.id)).where(*open_company_filters)) or 0
    college = (
        db.scalar(
            select(func.count(Company.id)).where(
                *open_company_filters,
                Company.accepts_college.is_(True),
            )
        )
        or 0
    )
    bachelor = (
        db.scalar(
            select(func.count(Company.id)).where(
                *open_company_filters,
                Company.accepts_bachelor.is_(True),
            )
        )
        or 0
    )
    new_jobs = (
        db.scalar(
            select(func.count(Job.id)).where(
                *open_job_filters,
                func.date(Job.created_at) == now.date(),
            )
        )
        or 0
    )
    app_total = (
        db.scalar(select(func.count(Application.id)).where(Application.user_id == user.id)) or 0
    )
    interview_total = (
        db.scalar(select(func.count(Interview.id)).where(Interview.user_id == user.id)) or 0
    )
    offer_total = db.scalar(select(func.count(Offer.id)).where(Offer.user_id == user.id)) or 0
    expiring = (
        db.scalar(
            select(func.count(Job.id)).where(
                *open_job_filters,
                Job.deadline >= now,
                Job.deadline <= soon,
            )
        )
        or 0
    )

    industry_rows = db.execute(
        select(Company.industry, func.count(Company.id))
        .group_by(Company.industry)
        .order_by(func.count(Company.id).desc())
        .limit(10)
    ).all()
    recent_rows = db.execute(
        select(Application, Job.title, Company.name)
        .join(Job, Application.job_id == Job.id)
        .join(Company, Job.company_id == Company.id)
        .where(Application.user_id == user.id)
        .order_by(Application.created_at.desc())
        .limit(5)
    ).all()

    trend: list[ApplicationTrendPoint] = []
    for offset in range(6, -1, -1):
        day = (now - timedelta(days=offset)).date()
        count = (
            db.scalar(
                select(func.count(Application.id)).where(
                    Application.user_id == user.id,
                    func.date(Application.created_at) == day,
                )
            )
            or 0
        )
        trend.append(ApplicationTrendPoint(date=day, count=count))

    return DashboardStats(
        open_companies=company_total,
        college_companies=college,
        bachelor_companies=bachelor,
        new_jobs_today=new_jobs,
        applications=app_total,
        interviews=interview_total,
        offers=offer_total,
        expiring_jobs=expiring,
        application_trend=trend,
        industry_distribution=[
            IndustryDistributionItem(industry=industry, count=count)
            for industry, count in industry_rows
        ],
        recent_applications=[
            RecentApplication(
                id=application.id,
                job_id=application.job_id,
                job_title=job_title,
                company_name=company_name,
                status=application.status,
                applied_at=application.applied_at,
            )
            for application, job_title, company_name in recent_rows
        ],
    )
