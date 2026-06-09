from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from signal_forge_api.config import Settings
from signal_forge_api.db import Base
from signal_forge_api.models import Company, Filing
from signal_forge_api.sec_client import SecCompany, SecFiling
from signal_forge_api.services import sync_company_from_sec


class FakeSecClient:
    def __init__(self) -> None:
        self.company = SecCompany(
            ticker="AAPL",
            cik=320193,
            cik_padded="0000320193",
            name="Apple Inc.",
            exchange="Nasdaq",
        )

    def search_companies(self, _ticker: str, *, limit: int = 1) -> list[SecCompany]:
        return [self.company][:limit]

    def fetch_submissions(self, _cik_padded: str) -> dict[str, object]:
        return {
            "name": "Apple Inc.",
            "sic": "3571",
            "fiscalYearEnd": "0928",
        }

    def fetch_recent_filings(self, _company: SecCompany, *, limit: int = 100) -> list[SecFiling]:
        return [
            SecFiling(
                accession_number="0000320193-24-000123",
                form="10-K",
                filing_date=date(2024, 11, 1),
                report_date=date(2024, 9, 28),
                primary_document="aapl-20240928.htm",
                primary_doc_description="10-K",
                source_url="https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm",
            )
        ][:limit]


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return session_factory()


def test_sync_company_persists_company_and_filings(monkeypatch) -> None:
    db = make_session()
    settings = Settings()
    monkeypatch.setattr(
        "signal_forge_api.services.get_sec_client", lambda _settings: FakeSecClient()
    )

    company, synced = sync_company_from_sec("AAPL", db, settings)

    assert synced == 1
    assert company.ticker == "AAPL"
    assert company.cik_padded == "0000320193"
    assert company.sic == "3571"
    assert company.fiscal_year_end == "0928"

    filing = db.scalar(select(Filing).where(Filing.company_id == company.id))

    assert filing is not None
    assert filing.form == "10-K"
    assert filing.primary_document == "aapl-20240928.htm"


def test_sync_company_is_idempotent(monkeypatch) -> None:
    db = make_session()
    settings = Settings()
    monkeypatch.setattr(
        "signal_forge_api.services.get_sec_client", lambda _settings: FakeSecClient()
    )

    sync_company_from_sec("AAPL", db, settings)
    sync_company_from_sec("AAPL", db, settings)

    companies = list(db.scalars(select(Company)))
    filings = list(db.scalars(select(Filing)))

    assert len(companies) == 1
    assert len(filings) == 1
