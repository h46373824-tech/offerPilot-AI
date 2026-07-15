"""Phase 3 trusted data sources, imports and verification."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="authorized_csv"),
        sa.Column("base_url", sa.String(500)),
        sa.Column("authorization_note", sa.Text(), nullable=False),
        sa.Column("license_info", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("last_import_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_data_sources_name", "data_sources", ["name"], unique=True)
    op.create_index("ix_data_sources_is_active", "data_sources", ["is_active"])
    op.create_index("ix_data_sources_created_by", "data_sources", ["created_by"])

    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("data_sources.id", ondelete="SET NULL")),
        sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="processing"),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_import_batches_source_id", "import_batches", ["source_id"])
    op.create_index("ix_import_batches_uploaded_by", "import_batches", ["uploaded_by"])
    op.create_index("ix_import_batches_entity_type", "import_batches", ["entity_type"])
    op.create_index("ix_import_batches_status", "import_batches", ["status"])

    for table in ("companies", "jobs"):
        op.add_column(table, sa.Column("data_source_id", sa.Integer(), nullable=True))
        op.create_index(f"ix_{table}_data_source_id", table, ["data_source_id"])
        op.create_foreign_key(
            f"fk_{table}_data_source_id_data_sources",
            table,
            "data_sources",
            ["data_source_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    for table in ("jobs", "companies"):
        op.drop_constraint(f"fk_{table}_data_source_id_data_sources", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_data_source_id", table_name=table)
        op.drop_column(table, "data_source_id")
    op.drop_table("import_batches")
    op.drop_table("data_sources")
