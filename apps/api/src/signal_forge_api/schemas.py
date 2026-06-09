"""API schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str


class CompanySearchResult(BaseModel):
    """Company search result from SEC metadata."""

    ticker: str
    cik: int
    cik_padded: str
    name: str
    exchange: str | None = None


class CompanyResponse(BaseModel):
    """Persisted company response."""

    id: int
    ticker: str
    cik: int
    cik_padded: str
    name: str
    exchange: str | None
    sic: str | None
    fiscal_year_end: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FilingResponse(BaseModel):
    """Persisted filing response."""

    id: int
    accession_number: str
    form: str
    filing_date: date | None
    report_date: date | None
    primary_document: str | None
    primary_doc_description: str | None
    source_url: str | None
    artifact: "FilingArtifactResponse | None" = None

    model_config = ConfigDict(from_attributes=True)


class FilingArtifactResponse(BaseModel):
    """Stored raw filing artifact response."""

    id: int
    object_key: str
    source_url: str
    content_type: str | None
    byte_size: int
    sha256: str
    downloaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanySyncResponse(BaseModel):
    """Company sync result."""

    company: CompanyResponse
    filings_synced: int
