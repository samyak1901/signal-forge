"""FastAPI application entrypoint."""

from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from signal_forge_api.config import Settings, get_settings
from signal_forge_api.db import get_db
from signal_forge_api.schemas import (
    CompanyResponse,
    CompanySearchResult,
    CompanySyncResponse,
    FilingArtifactResponse,
    FilingResponse,
    HealthResponse,
)
from signal_forge_api.services import (
    download_filing_artifact,
    get_company_by_ticker,
    get_company_filing,
    list_company_filings,
    search_sec_companies,
    sync_company_from_sec,
)

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


app = FastAPI(
    title="SignalForge API",
    description="SEC-first backend for the SignalForge research platform.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Return service health."""
    return HealthResponse(status="ok", service="signal-forge-api")


@app.get("/api/v1/companies/search", response_model=list[CompanySearchResult], tags=["companies"])
def search_companies(
    settings: AppSettings,
    q: Annotated[str, Query(min_length=1)],
) -> list[CompanySearchResult]:
    """Search SEC company metadata."""
    return [
        CompanySearchResult(**company.__dict__) for company in search_sec_companies(q, settings)
    ]


@app.post("/api/v1/companies/{ticker}/sync", response_model=CompanySyncResponse, tags=["companies"])
def sync_company(
    ticker: str,
    db: DbSession,
    settings: AppSettings,
) -> CompanySyncResponse:
    """Sync a company and recent filings from SEC."""
    try:
        company, filings_synced = sync_company_from_sec(ticker, db, settings)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CompanySyncResponse(
        company=CompanyResponse.model_validate(company), filings_synced=filings_synced
    )


@app.get("/api/v1/companies/{ticker}", response_model=CompanyResponse, tags=["companies"])
def get_company(ticker: str, db: DbSession) -> CompanyResponse:
    """Return a synced company by ticker."""
    company = get_company_by_ticker(ticker, db)
    if company is None:
        raise HTTPException(status_code=404, detail=f"Company {ticker.upper()} has not been synced")
    return CompanyResponse.model_validate(company)


@app.get(
    "/api/v1/companies/{ticker}/filings",
    response_model=list[FilingResponse],
    tags=["filings"],
)
def get_company_filings(ticker: str, db: DbSession) -> list[FilingResponse]:
    """Return filings for a synced company."""
    filings = list_company_filings(ticker, db)
    if filings is None:
        raise HTTPException(status_code=404, detail=f"Company {ticker.upper()} has not been synced")
    return [FilingResponse.model_validate(filing) for filing in filings]


@app.get(
    "/api/v1/companies/{ticker}/filings/{filing_id}",
    response_model=FilingResponse,
    tags=["filings"],
)
def get_company_filing_detail(ticker: str, filing_id: int, db: DbSession) -> FilingResponse:
    """Return a filing detail record with artifact status."""
    filing = get_company_filing(ticker, filing_id, db)
    if filing is None:
        raise HTTPException(status_code=404, detail="Filing not found")
    return FilingResponse.model_validate(filing)


@app.post(
    "/api/v1/companies/{ticker}/filings/{filing_id}/download",
    response_model=FilingArtifactResponse,
    tags=["filings"],
)
def download_company_filing(
    ticker: str,
    filing_id: int,
    db: DbSession,
    settings: AppSettings,
) -> FilingArtifactResponse:
    """Download and store a filing's primary SEC document."""
    try:
        artifact = download_filing_artifact(ticker, filing_id, db, settings)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if artifact is None:
        raise HTTPException(status_code=404, detail="Filing not found")
    return FilingArtifactResponse.model_validate(artifact)


def main() -> None:
    """Run the API with uvicorn."""
    uvicorn.run("signal_forge_api.main:app", host="0.0.0.0", port=8000, reload=True)  # noqa: S104


if __name__ == "__main__":
    main()
