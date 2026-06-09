"""create filing artifacts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_create_filing_artifacts"
down_revision: str | None = "0001_create_company_filings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        "filing_artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filing_id", sa.Integer(), nullable=False),
        sa.Column("object_key", sa.String(length=1024), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=True),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["filing_id"], ["filings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_filing_artifacts_filing_id"),
        "filing_artifacts",
        ["filing_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_filing_artifacts_object_key"),
        "filing_artifacts",
        ["object_key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_filing_artifacts_sha256"), "filing_artifacts", ["sha256"], unique=False
    )


def downgrade() -> None:
    """Revert migration."""
    op.drop_index(op.f("ix_filing_artifacts_sha256"), table_name="filing_artifacts")
    op.drop_index(op.f("ix_filing_artifacts_object_key"), table_name="filing_artifacts")
    op.drop_index(op.f("ix_filing_artifacts_filing_id"), table_name="filing_artifacts")
    op.drop_table("filing_artifacts")
