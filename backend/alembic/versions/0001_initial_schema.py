"""Initial OfferPilot schema."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _timestamps() -> tuple[sa.Column[sa.DateTime], sa.Column[sa.DateTime]]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("industry", sa.String(100), nullable=False),
        sa.Column("company_type", sa.String(100), nullable=False),
        sa.Column("website", sa.String(500)),
        sa.Column("campus_website", sa.String(500)),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("recruitment_status", sa.String(50), nullable=False),
        sa.Column("open_date", sa.Date()),
        sa.Column("deadline", sa.Date()),
        sa.Column("education_requirement", sa.String(100), nullable=False),
        sa.Column("accepts_college", sa.Boolean(), nullable=False),
        sa.Column("accepts_bachelor", sa.Boolean(), nullable=False),
        sa.Column("major_requirement", sa.Text()),
        sa.Column("work_cities", sa.String(500), nullable=False),
        sa.Column("data_source", sa.String(200), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True)),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    for column in ("name", "industry", "recruitment_status", "deadline", "is_demo"):
        op.create_index(f"ix_companies_{column}", "companies", [column])

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("work_cities", sa.String(500), nullable=False),
        sa.Column("education_requirement", sa.String(100), nullable=False),
        sa.Column("major_requirement", sa.Text()),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("requirements", sa.Text(), nullable=False),
        sa.Column("application_url", sa.String(500)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("deadline", sa.DateTime(timezone=True)),
        sa.Column("recruitment_status", sa.String(50), nullable=False),
        sa.Column("data_source", sa.String(200), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True)),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    for column in (
        "company_id",
        "title",
        "category",
        "work_cities",
        "education_requirement",
        "deadline",
        "recruitment_status",
        "is_demo",
    ):
        op.create_index(f"ix_jobs_{column}", "jobs", [column])
    op.create_index("ix_jobs_search", "jobs", ["title", "category", "work_cities"])

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("version", sa.String(50)),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        *_timestamps(),
        sa.UniqueConstraint("user_id", "job_id"),
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_job_id", "favorites", ["job_id"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            sa.Integer(),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("channel", sa.String(100)),
        sa.Column("notes", sa.Text()),
        *_timestamps(),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_job_id", "applications", ["job_id"])
    op.create_index("ix_applications_status", "applications", ["status"])

    op.create_table(
        "interviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("interview_type", sa.String(100), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("location", sa.String(300)),
        sa.Column("notes", sa.Text()),
        *_timestamps(),
    )
    for column in ("user_id", "application_id", "scheduled_at", "status"):
        op.create_index(f"ix_interviews_{column}", "interviews", [column])

    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("compensation", sa.String(200)),
        sa.Column("location", sa.String(200)),
        sa.Column("received_at", sa.Date(), nullable=False),
        sa.Column("response_deadline", sa.Date()),
        sa.Column("notes", sa.Text()),
        *_timestamps(),
    )
    for column in ("user_id", "application_id", "status"):
        op.create_index(f"ix_offers_{column}", "offers", [column])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])

    op.create_table(
        "job_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_job_alerts_user_id", "job_alerts", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("details", sa.JSON()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    for table in (
        "audit_logs",
        "job_alerts",
        "notifications",
        "offers",
        "interviews",
        "applications",
        "favorites",
        "resumes",
        "jobs",
        "companies",
        "users",
    ):
        op.drop_table(table)
