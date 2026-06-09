"""FastAPI application entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from signal_forge_api.config import Settings, get_settings
from signal_forge_api.db import create_tables, get_db
from signal_forge_api.schemas import (
    CompanyResponse,
    CompanySearchResult,
    CompanySyncResponse,
    FilingResponse,
    HealthResponse,
)
from signal_forge_api.services import (
    get_company_by_ticker,
    list_company_filings,
    search_sec_companies,
    sync_company_from_sec,
)

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialize phase-one application resources."""
    create_tables()
    yield


app = FastAPI(
    title="SignalForge API",
    description="SEC-first backend for the SignalForge research platform.",
    version="0.1.0",
    lifespan=lifespan,
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


def main() -> None:
    """Run the API with uvicorn."""
    uvicorn.run("signal_forge_api.main:app", host="0.0.0.0", port=8000, reload=True)  # noqa: S104


if __name__ == "__main__":
    main()
