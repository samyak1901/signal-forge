"""Application services."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from signal_forge_api.config import Settings
from signal_forge_api.models import Company, Filing
from signal_forge_api.sec_client import SecClient, SecCompany, SecFiling


def get_sec_client(settings: Settings) -> SecClient:
    """Build an SEC client from settings."""
    return SecClient(
        base_url=str(settings.sec_base_url),
        data_url=str(settings.sec_data_url),
        user_agent=settings.sec_user_agent,
        timeout_seconds=settings.sec_timeout_seconds,
    )


def search_sec_companies(query: str, settings: Settings) -> list[SecCompany]:
    """Search SEC company metadata."""
    return get_sec_client(settings).search_companies(query)


def sync_company_from_sec(ticker: str, db: Session, settings: Settings) -> tuple[Company, int]:
    """Sync company and recent filing metadata from SEC."""
    sec_client = get_sec_client(settings)
    matches = sec_client.search_companies(ticker, limit=1)
    if not matches or matches[0].ticker != ticker.upper():
        msg = f"No exact SEC ticker match found for {ticker}"
        raise LookupError(msg)

    sec_company = matches[0]
    submissions = sec_client.fetch_submissions(sec_company.cik_padded)
    company = _upsert_company(db, sec_company, submissions)
    filings = sec_client.fetch_recent_filings(sec_company, limit=100)
    synced = 0
    for filing in filings:
        _upsert_filing(db, company, filing)
        synced += 1
    db.commit()
    db.refresh(company)
    return company, synced


def get_company_by_ticker(ticker: str, db: Session) -> Company | None:
    """Return a persisted company by ticker."""
    return db.scalar(select(Company).where(Company.ticker == ticker.upper()))


def list_company_filings(ticker: str, db: Session) -> list[Filing] | None:
    """List filings for a persisted company by ticker."""
    company = get_company_by_ticker(ticker, db)
    if company is None:
        return None
    return list(
        db.scalars(
            select(Filing)
            .where(Filing.company_id == company.id)
            .order_by(Filing.filing_date.desc())
        )
    )


def _upsert_company(
    db: Session, sec_company: SecCompany, submissions: dict[str, object]
) -> Company:
    company = db.scalar(select(Company).where(Company.ticker == sec_company.ticker))
    if company is None:
        company = Company(
            ticker=sec_company.ticker,
            cik=sec_company.cik,
            cik_padded=sec_company.cik_padded,
            name=sec_company.name,
        )
        db.add(company)

    company.cik = sec_company.cik
    company.cik_padded = sec_company.cik_padded
    company.name = str(submissions.get("name") or sec_company.name)
    company.exchange = sec_company.exchange
    company.sic = _optional_string(submissions.get("sic"))
    company.fiscal_year_end = _optional_string(submissions.get("fiscalYearEnd"))
    db.flush()
    return company


def _upsert_filing(db: Session, company: Company, filing: SecFiling) -> Filing:
    accession_number = filing.accession_number
    existing = db.scalar(
        select(Filing).where(
            Filing.company_id == company.id,
            Filing.accession_number == accession_number,
        )
    )
    if existing is None:
        existing = Filing(company_id=company.id, accession_number=accession_number, form="UNKNOWN")
        db.add(existing)

    existing.form = filing.form
    existing.filing_date = filing.filing_date
    existing.report_date = filing.report_date
    existing.primary_document = filing.primary_document
    existing.primary_doc_description = filing.primary_doc_description
    existing.source_url = filing.source_url
    return existing


def _optional_string(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value)
