from datetime import date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from signal_forge_api.config import Settings
from signal_forge_api.db import Base
from signal_forge_api.models import Company, Filing, FilingArtifact
from signal_forge_api.sec_client import SecCompany, SecDocument, SecFiling
from signal_forge_api.services import download_filing_artifact, sync_company_from_sec


class FakeObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put_bytes(self, key: str, content: bytes, content_type: str | None) -> None:
        _ = content_type
        self.objects[key] = content


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

    def fetch_document(self, _source_url: str) -> SecDocument:
        return SecDocument(content=b"<html>Apple filing</html>", content_type="text/html")


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


def test_download_filing_artifact_stores_raw_document(monkeypatch) -> None:
    db = make_session()
    settings = Settings()
    object_store = FakeObjectStore()
    monkeypatch.setattr(
        "signal_forge_api.services.get_sec_client", lambda _settings: FakeSecClient()
    )
    company, _synced = sync_company_from_sec("AAPL", db, settings)
    filing = db.scalar(select(Filing).where(Filing.company_id == company.id))

    assert filing is not None

    artifact = download_filing_artifact("AAPL", filing.id, db, settings, object_store)

    assert artifact is not None
    assert artifact.byte_size == len(b"<html>Apple filing</html>")
    assert artifact.content_type == "text/html"
    assert artifact.object_key in object_store.objects
    assert object_store.objects[artifact.object_key] == b"<html>Apple filing</html>"


def test_download_filing_artifact_is_idempotent(monkeypatch) -> None:
    db = make_session()
    settings = Settings()
    object_store = FakeObjectStore()
    monkeypatch.setattr(
        "signal_forge_api.services.get_sec_client", lambda _settings: FakeSecClient()
    )
    company, _synced = sync_company_from_sec("AAPL", db, settings)
    filing = db.scalar(select(Filing).where(Filing.company_id == company.id))

    assert filing is not None

    first = download_filing_artifact("AAPL", filing.id, db, settings, object_store)
    second = download_filing_artifact("AAPL", filing.id, db, settings, object_store)
    artifacts = list(db.scalars(select(FilingArtifact)))

    assert first is not None
    assert second is not None
    assert first.id == second.id
    assert len(artifacts) == 1
