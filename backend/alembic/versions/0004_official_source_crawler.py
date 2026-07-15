"""Official recruitment source crawler configuration and runs."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("data_sources", sa.Column("company_id", sa.Integer(), nullable=True))
    op.add_column("data_sources", sa.Column("feed_url", sa.String(1000), nullable=True))
    op.add_column(
        "data_sources",
        sa.Column("parser_mode", sa.String(30), nullable=False, server_default="auto"),
    )
    op.add_column(
        "data_sources",
        sa.Column("link_keywords", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )
    op.add_column(
        "data_sources",
        sa.Column("is_crawl_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "data_sources",
        sa.Column("crawl_interval_minutes", sa.Integer(), nullable=False, server_default="360"),
    )
    op.add_column("data_sources", sa.Column("last_crawled_at", sa.DateTime(timezone=True)))
    op.add_column("data_sources", sa.Column("next_crawl_at", sa.DateTime(timezone=True)))
    op.add_column("data_sources", sa.Column("last_crawl_status", sa.String(30)))
    op.create_index("ix_data_sources_company_id", "data_sources", ["company_id"])
    op.create_index("ix_data_sources_is_crawl_enabled", "data_sources", ["is_crawl_enabled"])
    op.create_index("ix_data_sources_next_crawl_at", "data_sources", ["next_crawl_at"])
    op.create_foreign_key(
        "fk_data_sources_company_id_companies",
        "data_sources",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "crawl_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("data_sources.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(30), nullable=False, server_default="running"),
        sa.Column("discovered_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_crawl_runs_source_id", "crawl_runs", ["source_id"])
    op.create_index("ix_crawl_runs_status", "crawl_runs", ["status"])


def downgrade() -> None:
    op.drop_table("crawl_runs")
    op.drop_constraint("fk_data_sources_company_id_companies", "data_sources", type_="foreignkey")
    op.drop_index("ix_data_sources_next_crawl_at", table_name="data_sources")
    op.drop_index("ix_data_sources_is_crawl_enabled", table_name="data_sources")
    op.drop_index("ix_data_sources_company_id", table_name="data_sources")
    for column in (
        "last_crawl_status",
        "next_crawl_at",
        "last_crawled_at",
        "crawl_interval_minutes",
        "is_crawl_enabled",
        "link_keywords",
        "parser_mode",
        "feed_url",
        "company_id",
    ):
        op.drop_column("data_sources", column)
