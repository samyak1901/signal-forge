"""Application services."""

from datetime import UTC, datetime
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.orm import Session

from signal_forge_api.config import Settings
from signal_forge_api.models import Company, Filing, FilingArtifact
from signal_forge_api.object_store import ObjectStore, get_object_store
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


def get_company_filing(ticker: str, filing_id: int, db: Session) -> Filing | None:
    """Return a single filing for a synced company."""
    company = get_company_by_ticker(ticker, db)
    if company is None:
        return None
    return db.scalar(select(Filing).where(Filing.company_id == company.id, Filing.id == filing_id))


def download_filing_artifact(
    ticker: str,
    filing_id: int,
    db: Session,
    settings: Settings,
    object_store: ObjectStore | None = None,
) -> FilingArtifact | None:
    """Download a filing's primary document into object storage."""
    filing = get_company_filing(ticker, filing_id, db)
    if filing is None:
        return None
    existing_artifact = db.scalar(
        select(FilingArtifact).where(FilingArtifact.filing_id == filing.id)
    )
    if existing_artifact is not None:
        return existing_artifact
    if not filing.source_url:
        msg = f"Filing {filing_id} has no source URL"
        raise ValueError(msg)

    sec_document = get_sec_client(settings).fetch_document(filing.source_url)
    digest = sha256(sec_document.content).hexdigest()
    object_key = _filing_object_key(filing)
    store = object_store or get_object_store(settings)
    store.put_bytes(object_key, sec_document.content, sec_document.content_type)

    artifact = FilingArtifact(
        filing_id=filing.id,
        object_key=object_key,
        source_url=filing.source_url,
        content_type=sec_document.content_type,
        byte_size=len(sec_document.content),
        sha256=digest,
        downloaded_at=datetime.now(UTC),
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


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


def _filing_object_key(filing: Filing) -> str:
    company = filing.company
    document = filing.primary_document or f"{filing.accession_number}.txt"
    accession = filing.accession_number.replace("-", "")
    return f"sec/{company.ticker}/{filing.form}/{accession}/{document}"
