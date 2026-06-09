const pipelineSteps = [
  "Resolve ticker to CIK",
  "Fetch SEC submissions",
  "Persist filing metadata",
  "Download primary filing",
  "Extract sections",
  "Generate citations",
];

const sourceTypes = ["10-K", "10-Q", "8-K", "DEF 14A", "Manual transcript", "GDELT news"];

export function App() {
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
            <input id="ticker" name="ticker" placeholder="AAPL" aria-label="Ticker symbol" />
            <button type="button">Sync SEC Data</button>
          </div>
          <p>
            Phase one connects this flow to the FastAPI SEC sync endpoint. The UI shell is ready for
            company search, filing status, research runs, and citations.
          </p>
        </div>
      </section>

      <section className="grid" aria-label="Platform overview">
        <article className="panel span-2">
          <p className="eyebrow">Pipeline</p>
          <h2>SEC-first ingestion path</h2>
          <ol className="steps">
            {pipelineSteps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
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
