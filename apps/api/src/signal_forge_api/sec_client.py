"""Client for public SEC data APIs."""

from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx


@dataclass(frozen=True)
class SecDocument:
    """Downloaded SEC document bytes and response metadata."""

    content: bytes
    content_type: str | None


@dataclass(frozen=True)
class SecCompany:
    """Company metadata from SEC ticker mapping files."""

    ticker: str
    cik: int
    cik_padded: str
    name: str
    exchange: str | None = None


@dataclass(frozen=True)
class SecFiling:
    """Filing metadata from the SEC submissions API."""

    accession_number: str
    form: str
    filing_date: date | None
    report_date: date | None
    primary_document: str | None
    primary_doc_description: str | None
    source_url: str | None


class SecClient:
    """Small SEC API client with explicit User-Agent handling."""

    def __init__(
        self,
        *,
        base_url: str,
        data_url: str,
        user_agent: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        """Initialize the client with base URLs and SEC-required headers."""
        self._base_url = base_url.rstrip("/")
        self._data_url = data_url.rstrip("/")
        self._headers = {
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": user_agent,
        }
        self._timeout = timeout_seconds

    def search_companies(self, query: str, *, limit: int = 10) -> list[SecCompany]:
        """Search SEC company ticker metadata by ticker or company name."""
        normalized_query = query.strip().upper()
        companies = self.fetch_company_tickers(exchange_data=True)
        exact = [company for company in companies if company.ticker == normalized_query]
        if exact:
            return exact[:limit]

        lowered = query.strip().lower()
        matches = [
            company
            for company in companies
            if lowered in company.ticker.lower() or lowered in company.name.lower()
        ]
        return matches[:limit]

    def fetch_company_tickers(self, *, exchange_data: bool = False) -> list[SecCompany]:
        """Fetch company ticker mappings from SEC files."""
        path = (
            "/files/company_tickers_exchange.json"
            if exchange_data
            else "/files/company_tickers.json"
        )
        payload = self._get_json(f"{self._base_url}{path}")
        if exchange_data:
            return self._parse_exchange_tickers(payload)
        return self._parse_company_tickers(payload)

    def fetch_submissions(self, cik_padded: str) -> dict[str, Any]:
        """Fetch SEC submissions JSON for a padded CIK."""
        return self._get_json(f"{self._data_url}/submissions/CIK{cik_padded}.json")

    def fetch_recent_filings(self, company: SecCompany, *, limit: int = 100) -> list[SecFiling]:
        """Fetch recent filing metadata for a company."""
        payload = self.fetch_submissions(company.cik_padded)
        recent = payload.get("filings", {}).get("recent", {})
        accessions = recent.get("accessionNumber", [])[:limit]
        forms = recent.get("form", [])[:limit]
        filing_dates = recent.get("filingDate", [])[:limit]
        report_dates = recent.get("reportDate", [])[:limit]
        primary_documents = recent.get("primaryDocument", [])[:limit]
        descriptions = recent.get("primaryDocDescription", [])[:limit]

        filings: list[SecFiling] = []
        for index, accession_number in enumerate(accessions):
            primary_document = self._value_at(primary_documents, index)
            filings.append(
                SecFiling(
                    accession_number=accession_number,
                    form=self._value_at(forms, index) or "UNKNOWN",
                    filing_date=self._parse_date(self._value_at(filing_dates, index)),
                    report_date=self._parse_date(self._value_at(report_dates, index)),
                    primary_document=primary_document,
                    primary_doc_description=self._value_at(descriptions, index),
                    source_url=self.build_filing_url(
                        company.cik, accession_number, primary_document
                    ),
                )
            )
        return filings

    def fetch_company_facts(self, cik_padded: str) -> dict[str, Any]:
        """Fetch XBRL company facts for a padded CIK."""
        return self._get_json(f"{self._data_url}/api/xbrl/companyfacts/CIK{cik_padded}.json")

    def fetch_document(self, url: str) -> SecDocument:
        """Fetch a raw SEC filing document."""
        with httpx.Client(
            headers=self._headers, timeout=self._timeout, follow_redirects=True
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return SecDocument(
                content=response.content,
                content_type=response.headers.get("content-type"),
            )

    def build_filing_url(
        self, cik: int, accession_number: str, primary_document: str | None
    ) -> str | None:
        """Build the SEC archive URL for a primary filing document."""
        if not primary_document:
            return None
        accession_without_dashes = accession_number.replace("-", "")
        return (
            f"{self._base_url}/Archives/edgar/data/{cik}/"
            f"{accession_without_dashes}/{primary_document}"
        )

    def _get_json(self, url: str) -> dict[str, Any]:
        with httpx.Client(
            headers=self._headers, timeout=self._timeout, follow_redirects=True
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                msg = f"Expected JSON object from SEC endpoint: {url}"
                raise TypeError(msg)
            return payload

    @staticmethod
    def _parse_company_tickers(payload: dict[str, Any]) -> list[SecCompany]:
        companies: list[SecCompany] = []
        for row in payload.values():
            cik = int(row["cik_str"])
            companies.append(
                SecCompany(
                    ticker=str(row["ticker"]).upper(),
                    cik=cik,
                    cik_padded=f"{cik:010d}",
                    name=str(row["title"]),
                )
            )
        return companies

    @staticmethod
    def _parse_exchange_tickers(payload: dict[str, Any]) -> list[SecCompany]:
        fields = payload.get("fields", [])
        data = payload.get("data", [])
        companies: list[SecCompany] = []
        for row in data:
            values = dict(zip(fields, row, strict=False))
            cik = int(values["cik"])
            companies.append(
                SecCompany(
                    ticker=str(values["ticker"]).upper(),
                    cik=cik,
                    cik_padded=f"{cik:010d}",
                    name=str(values["name"]),
                    exchange=str(values["exchange"]) if values.get("exchange") else None,
                )
            )
        return companies

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        return date.fromisoformat(value)

    @staticmethod
    def _value_at(values: list[Any], index: int) -> Any | None:
        if index >= len(values):
            return None
        value = values[index]
        return value if value != "" else None
