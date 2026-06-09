# Data Sources

SignalForge starts with verified public sources and treats vendor data as optional integrations.

## SEC Sources

### Ticker Mapping

```txt
https://www.sec.gov/files/company_tickers.json
https://www.sec.gov/files/company_tickers_exchange.json
```

Used for:

- ticker lookup
- CIK resolution
- exchange metadata
- company names

### Submissions API

```txt
https://data.sec.gov/submissions/CIK##########.json
```

Used for:

- filing history
- form type
- accession number
- filing date
- report date
- primary document name

### Company Facts API

```txt
https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
```

Used for:

- standardized financial facts
- taxonomy concepts
- units
- periods
- source filings

### Filing Archives

```txt
https://www.sec.gov/Archives/edgar/data/{cik}/{accession_without_dashes}/{primary_document}
```

Used for:

- raw filing HTML
- raw filing TXT
- source-backed citations

## SEC Access Rules

SEC requests must include a declared `User-Agent` and stay within fair-access limits. The current public limit is 10 requests per second. SignalForge should cache responses and request only what it needs.

## Later Sources

### Manual Uploads

Manual uploads are the safest initial path for transcripts, investor presentations, PDFs, and personal notes.

### GDELT

GDELT DOC 2.0 can provide public news discovery, article metadata, timelines, and tone. It should be used as discovery metadata first, not as a hidden article-scraping system.

### FRED

FRED provides macroeconomic time series through an API key.

### FMP And Quartr

FMP and Quartr can provide transcript and market-data integrations later. These are vendor-backed connectors and should be optional.
