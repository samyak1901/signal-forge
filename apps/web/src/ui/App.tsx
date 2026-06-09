import { useState } from "react";

import type { Company, CompanySearchResult, Filing } from "../api";
import { getCompanyFilings, searchCompanies, syncCompany } from "../api";

const pipelineSteps = [
  "Resolve ticker to CIK",
  "Fetch SEC submissions",
  "Persist filing metadata",
  "Download primary filing",
  "Extract sections",
  "Generate citations",
];

const sourceTypes = ["10-K", "10-Q", "8-K", "DEF 14A", "Manual transcript", "GDELT news"];

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong";
}

export function App() {
  const [query, setQuery] = useState("AAPL");
  const [matches, setMatches] = useState<CompanySearchResult[]>([]);
  const [company, setCompany] = useState<Company | null>(null);
  const [filings, setFilings] = useState<Filing[]>([]);
  const [status, setStatus] = useState("Ready to sync SEC filing metadata.");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSearch() {
    const normalized = query.trim().toUpperCase();
    if (!normalized) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setStatus(`Searching SEC company metadata for ${normalized}...`);
    try {
      const results = await searchCompanies(normalized);
      setMatches(results);
      setStatus(
        results.length > 0 ? `Found ${results.length} SEC match(es).` : "No matches found.",
      );
    } catch (caught) {
      setError(getErrorMessage(caught));
      setStatus("Search failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSync(ticker = query) {
    const normalized = ticker.trim().toUpperCase();
    if (!normalized) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setStatus(`Syncing ${normalized} from SEC submissions...`);
    try {
      const result = await syncCompany(normalized);
      const syncedFilings = await getCompanyFilings(normalized);
      setQuery(normalized);
      setCompany(result.company);
      setFilings(syncedFilings);
      setStatus(`Synced ${result.filings_synced} recent SEC filings for ${normalized}.`);
    } catch (caught) {
      setError(getErrorMessage(caught));
      setStatus("Sync failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero-panel">
        <nav className="topbar" aria-label="Primary navigation">
          <div>
            <p className="eyebrow">SignalForge</p>
            <h1>Source-backed public-company research cockpit.</h1>
          </div>
          <a className="docs-link" href="/docs" aria-label="Open API docs when backend is running">
            API Docs
          </a>
        </nav>

        <div className="search-card">
          <label htmlFor="ticker">Research ticker</label>
          <div className="ticker-row">
            <input
              id="ticker"
              name="ticker"
              placeholder="AAPL"
              aria-label="Ticker symbol"
              value={query}
              onChange={(event) => setQuery(event.target.value.toUpperCase())}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  void handleSearch();
                }
              }}
            />
            <button type="button" disabled={isLoading} onClick={() => void handleSync()}>
              {isLoading ? "Working..." : "Sync SEC Data"}
            </button>
          </div>
          <div className="action-row">
            <button type="button" disabled={isLoading} onClick={() => void handleSearch()}>
              Search SEC
            </button>
            <span>{status}</span>
          </div>
          {error ? <p className="error">{error}</p> : null}

          {matches.length > 0 ? (
            <ul className="matches" aria-label="SEC company matches">
              {matches.map((match) => (
                <li key={`${match.ticker}-${match.cik}`}>
                  <button
                    type="button"
                    disabled={isLoading}
                    onClick={() => void handleSync(match.ticker)}
                  >
                    {match.ticker} · {match.name} {match.exchange ? `· ${match.exchange}` : ""}
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </section>

      <section className="grid" aria-label="Platform overview">
        <article className="panel span-2">
          <p className="eyebrow">Company</p>
          <h2>{company ? `${company.ticker} · ${company.name}` : "SEC filing workspace"}</h2>
          {company ? (
            <div className="company-grid">
              <span>CIK {company.cik_padded}</span>
              <span>{company.exchange ?? "Exchange unavailable"}</span>
              <span>SIC {company.sic ?? "unavailable"}</span>
              <span>FY end {company.fiscal_year_end ?? "unavailable"}</span>
            </div>
          ) : (
            <ol className="steps">
              {pipelineSteps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          )}

          {filings.length > 0 ? (
            <section className="filings-table" aria-label="Synced SEC filings">
              <div className="filings-header">
                <span>Form</span>
                <span>Filed</span>
                <span>Document</span>
              </div>
              {filings.slice(0, 12).map((filing) => (
                <a
                  className="filing-row"
                  href={filing.source_url ?? undefined}
                  key={filing.id}
                  rel="noreferrer"
                  target="_blank"
                >
                  <span>{filing.form}</span>
                  <span>{filing.filing_date ?? "Unknown"}</span>
                  <span>{filing.primary_document ?? filing.accession_number}</span>
                </a>
              ))}
            </section>
          ) : null}
        </article>

        <article className="panel">
          <p className="eyebrow">Sources</p>
          <h2>Planned library</h2>
          <div className="chips">
            {sourceTypes.map((source) => (
              <span key={source}>{source}</span>
            ))}
          </div>
        </article>

        <article className="panel">
          <p className="eyebrow">Architecture</p>
          <h2>Built like a platform</h2>
          <p>
            FastAPI owns the product API, Postgres persists metadata and runs, MinIO stores raw
            artifacts, and Qdrant will power source retrieval.
          </p>
        </article>
      </section>
    </main>
  );
}
