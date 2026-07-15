"""Phase 2 workflow, resume storage, alerts and reminders."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("graduation_year", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("education_level", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("target_cities", sa.String(length=500), nullable=True))
    op.add_column(
        "users",
        sa.Column("notifications_enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
    )

    op.add_column("applications", sa.Column("resume_id", sa.Integer(), nullable=True))
    op.create_index("ix_applications_resume_id", "applications", ["resume_id"])
    op.create_foreign_key(
        "fk_applications_resume_id_resumes",
        "applications",
        "resumes",
        ["resume_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("notifications", sa.Column("related_entity_type", sa.String(50)))
    op.add_column("notifications", sa.Column("related_entity_id", sa.Integer()))
    op.add_column("notifications", sa.Column("scheduled_for", sa.DateTime(timezone=True)))
    op.create_index("ix_notifications_scheduled_for", "notifications", ["scheduled_for"])

    op.add_column("resumes", sa.Column("original_filename", sa.String(255)))
    op.add_column("resumes", sa.Column("content_type", sa.String(100)))
    op.add_column("resumes", sa.Column("file_size", sa.Integer()))
    op.add_column("resumes", sa.Column("storage_key", sa.String(500)))
    op.add_column("resumes", sa.Column("checksum_sha256", sa.String(64)))
    op.execute(
        "UPDATE resumes SET original_filename = 'legacy-resume.pdf', "
        "content_type = 'application/pdf', file_size = 0, "
        "storage_key = 'legacy/' || id::text, "
        "checksum_sha256 = repeat('0', 64)"
    )
    for column in (
        "original_filename",
        "content_type",
        "file_size",
        "storage_key",
        "checksum_sha256",
    ):
        op.alter_column("resumes", column, nullable=False)
    op.create_unique_constraint("uq_resumes_storage_key", "resumes", ["storage_key"])

    op.add_column(
        "job_alerts",
        sa.Column("frequency", sa.String(30), server_default="daily", nullable=False),
    )
    op.add_column("job_alerts", sa.Column("last_run_at", sa.DateTime(timezone=True)))
    op.add_column("job_alerts", sa.Column("next_run_at", sa.DateTime(timezone=True)))
    op.create_index("ix_job_alerts_next_run_at", "job_alerts", ["next_run_at"])


def downgrade() -> None:
    op.drop_index("ix_job_alerts_next_run_at", table_name="job_alerts")
    op.drop_column("job_alerts", "next_run_at")
    op.drop_column("job_alerts", "last_run_at")
    op.drop_column("job_alerts", "frequency")

    op.drop_constraint("uq_resumes_storage_key", "resumes", type_="unique")
    op.drop_column("resumes", "checksum_sha256")
    op.drop_column("resumes", "storage_key")
    op.drop_column("resumes", "file_size")
    op.drop_column("resumes", "content_type")
    op.drop_column("resumes", "original_filename")

    op.drop_index("ix_notifications_scheduled_for", table_name="notifications")
    op.drop_column("notifications", "scheduled_for")
    op.drop_column("notifications", "related_entity_id")
    op.drop_column("notifications", "related_entity_type")

    op.drop_constraint("fk_applications_resume_id_resumes", "applications", type_="foreignkey")
    op.drop_index("ix_applications_resume_id", table_name="applications")
    op.drop_column("applications", "resume_id")

    op.drop_column("users", "notifications_enabled")
    op.drop_column("users", "target_cities")
    op.drop_column("users", "education_level")
    op.drop_column("users", "graduation_year")
