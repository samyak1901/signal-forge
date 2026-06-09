"""create company filings."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_company_filings"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply migration."""
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("cik", sa.Integer(), nullable=False),
        sa.Column("cik_padded", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("exchange", sa.String(length=64), nullable=True),
        sa.Column("sic", sa.String(length=16), nullable=True),
        sa.Column("fiscal_year_end", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_cik"), "companies", ["cik"], unique=True)
    op.create_index(op.f("ix_companies_cik_padded"), "companies", ["cik_padded"], unique=True)
    op.create_index(op.f("ix_companies_ticker"), "companies", ["ticker"], unique=True)

    op.create_table(
        "filings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("accession_number", sa.String(length=32), nullable=False),
        sa.Column("form", sa.String(length=32), nullable=False),
        sa.Column("filing_date", sa.Date(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("primary_document", sa.String(length=512), nullable=True),
        sa.Column("primary_doc_description", sa.String(length=512), nullable=True),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id", "accession_number"),
    )
    op.create_index(
        op.f("ix_filings_accession_number"), "filings", ["accession_number"], unique=False
    )
    op.create_index(op.f("ix_filings_company_id"), "filings", ["company_id"], unique=False)
    op.create_index(op.f("ix_filings_form"), "filings", ["form"], unique=False)


def downgrade() -> None:
    """Revert migration."""
    op.drop_index(op.f("ix_filings_form"), table_name="filings")
    op.drop_index(op.f("ix_filings_company_id"), table_name="filings")
    op.drop_index(op.f("ix_filings_accession_number"), table_name="filings")
    op.drop_table("filings")
    op.drop_index(op.f("ix_companies_ticker"), table_name="companies")
    op.drop_index(op.f("ix_companies_cik_padded"), table_name="companies")
    op.drop_index(op.f("ix_companies_cik"), table_name="companies")
    op.drop_table("companies")
