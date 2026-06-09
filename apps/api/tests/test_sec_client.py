from datetime import date

from signal_forge_api.sec_client import SecClient


def test_parse_exchange_tickers() -> None:
    payload = {
        "fields": ["cik", "name", "ticker", "exchange"],
        "data": [[320193, "Apple Inc.", "AAPL", "Nasdaq"]],
    }

    companies = SecClient._parse_exchange_tickers(payload)  # noqa: SLF001

    assert companies[0].ticker == "AAPL"
    assert companies[0].cik == 320193
    assert companies[0].cik_padded == "0000320193"
    assert companies[0].exchange == "Nasdaq"


def test_build_filing_url() -> None:
    client = SecClient(
        base_url="https://www.sec.gov",
        data_url="https://data.sec.gov",
        user_agent="SignalForge tests@example.com",
    )

    url = client.build_filing_url(320193, "0000320193-24-000123", "aapl-20240928.htm")

    assert url == (
        "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm"
    )


def test_parse_recent_filings_from_mocked_submissions(monkeypatch) -> None:
    client = SecClient(
        base_url="https://www.sec.gov",
        data_url="https://data.sec.gov",
        user_agent="SignalForge tests@example.com",
    )
    company = SecClient._parse_exchange_tickers(  # noqa: SLF001
        {
            "fields": ["cik", "name", "ticker", "exchange"],
            "data": [[320193, "Apple Inc.", "AAPL", "Nasdaq"]],
        }
    )[0]

    def fake_fetch_submissions(_cik_padded: str) -> dict[str, object]:
        return {
            "filings": {
                "recent": {
                    "accessionNumber": ["0000320193-24-000123"],
                    "form": ["10-K"],
                    "filingDate": ["2024-11-01"],
                    "reportDate": ["2024-09-28"],
                    "primaryDocument": ["aapl-20240928.htm"],
                    "primaryDocDescription": ["10-K"],
                }
            }
        }

    monkeypatch.setattr(client, "fetch_submissions", fake_fetch_submissions)

    filings = client.fetch_recent_filings(company)

    assert filings[0].form == "10-K"
    assert filings[0].filing_date == date(2024, 11, 1)
    assert filings[0].source_url is not None
