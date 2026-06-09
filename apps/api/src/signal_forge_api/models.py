"""Database models."""

from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from signal_forge_api.db import Base


class Company(Base):
    """A public company resolved through SEC metadata."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    cik: Mapped[int] = mapped_column(unique=True, index=True)
    cik_padded: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(512))
    exchange: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sic: Mapped[str | None] = mapped_column(String(16), nullable=True)
    fiscal_year_end: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=func.now()
    )

    filings: Mapped[list["Filing"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class Filing(Base):
    """SEC filing metadata for a company."""

    __tablename__ = "filings"
    __table_args__ = (UniqueConstraint("company_id", "accession_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    accession_number: Mapped[str] = mapped_column(String(32), index=True)
    form: Mapped[str] = mapped_column(String(32), index=True)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    primary_document: Mapped[str | None] = mapped_column(String(512), nullable=True)
    primary_doc_description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=func.now()
    )

    company: Mapped[Company] = relationship(back_populates="filings")
    artifact: Mapped["FilingArtifact | None"] = relationship(
        back_populates="filing", cascade="all, delete-orphan"
    )


class FilingArtifact(Base):
    """Raw filing artifact stored in object storage."""

    __tablename__ = "filing_artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    filing_id: Mapped[int] = mapped_column(ForeignKey("filings.id"), unique=True, index=True)
    object_key: Mapped[str] = mapped_column(String(1024), unique=True)
    source_url: Mapped[str] = mapped_column(String(1024))
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    byte_size: Mapped[int] = mapped_column(Integer)
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=func.now()
    )

    filing: Mapped[Filing] = relationship(back_populates="artifact")
