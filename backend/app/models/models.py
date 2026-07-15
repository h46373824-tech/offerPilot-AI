from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    graduation_year: Mapped[int | None]
    education_level: Mapped[str | None] = mapped_column(String(50))
    target_cities: Mapped[str | None] = mapped_column(String(500))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Company(TimestampMixin, Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    industry: Mapped[str] = mapped_column(String(100), index=True)
    company_type: Mapped[str] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(500))
    campus_website: Mapped[str | None] = mapped_column(String(500))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    recruitment_status: Mapped[str] = mapped_column(String(50), default="unverified", index=True)
    open_date: Mapped[date | None] = mapped_column(Date)
    deadline: Mapped[date | None] = mapped_column(Date, index=True)
    education_requirement: Mapped[str] = mapped_column(String(100))
    accepts_college: Mapped[bool] = mapped_column(Boolean, default=False)
    accepts_bachelor: Mapped[bool] = mapped_column(Boolean, default=True)
    major_requirement: Mapped[str | None] = mapped_column(Text)
    work_cities: Mapped[str] = mapped_column(String(500))
    data_source: Mapped[str] = mapped_column(String(200), default="manual")
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    jobs: Mapped[list["Job"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str] = mapped_column(String(100), index=True)
    work_cities: Mapped[str] = mapped_column(String(500), index=True)
    education_requirement: Mapped[str] = mapped_column(String(100), index=True)
    major_requirement: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text)
    application_url: Mapped[str | None] = mapped_column(String(500))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    recruitment_status: Mapped[str] = mapped_column(String(50), default="unverified", index=True)
    data_source: Mapped[str] = mapped_column(String(200), default="manual")
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    company: Mapped[Company] = relationship(back_populates="jobs")


class Favorite(TimestampMixin, Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "job_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)


class Application(TimestampMixin, Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[int | None] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="planned", index=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    channel: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)


class Interview(TimestampMixin, Base):
    __tablename__ = "interviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    interview_type: Mapped[str] = mapped_column(String(100))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", index=True)
    location: Mapped[str | None] = mapped_column(String(300))
    notes: Mapped[str | None] = mapped_column(Text)


class Offer(TimestampMixin, Base):
    __tablename__ = "offers"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    compensation: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(200))
    received_at: Mapped[date] = mapped_column(Date)
    response_deadline: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)


class Notification(TimestampMixin, Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    notification_type: Mapped[str] = mapped_column(String(50))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    related_entity_type: Mapped[str | None] = mapped_column(String(50))
    related_entity_id: Mapped[int | None]
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class Resume(TimestampMixin, Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    file_url: Mapped[str] = mapped_column(String(500))
    version: Mapped[str | None] = mapped_column(String(50))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    original_filename: Mapped[str] = mapped_column(String(255), default="resume.pdf")
    content_type: Mapped[str] = mapped_column(String(100), default="application/pdf")
    file_size: Mapped[int] = mapped_column(default=0)
    storage_key: Mapped[str] = mapped_column(String(500), unique=True)
    checksum_sha256: Mapped[str] = mapped_column(String(64))


class JobAlert(TimestampMixin, Base):
    __tablename__ = "job_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    criteria: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    frequency: Mapped[str] = mapped_column(String(30), default="daily")
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[int | None]
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


Index("ix_jobs_search", Job.title, Job.category, Job.work_cities)
