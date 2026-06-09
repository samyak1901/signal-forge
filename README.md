# SignalForge

SignalForge is a production-style AI research platform for public-company analysis. It starts with official SEC data, turns filings and financial facts into structured research context, and evolves into a source-backed research cockpit with ingestion pipelines, retrieval, agent workflows, and a Vite React dashboard.

The project is intentionally built like a real software platform rather than a demo chatbot. The first milestone focuses on a reliable SEC-first data foundation before adding RAG, research agents, transcripts, news, and additional services.

## What It Will Do

- Resolve public-company tickers to SEC CIK identifiers.
- Fetch filing history, company metadata, and standardized XBRL facts from SEC APIs.
- Download and index 10-K, 10-Q, 8-K, proxy, and other filings.
- Store raw artifacts, metadata, chunks, citations, and research runs.
- Generate source-backed research summaries and memos.
- Provide a web dashboard for company research, filings, run traces, and citations.

## Architecture

```txt
apps/web              Vite React dashboard
apps/api              FastAPI backend and OpenAPI surface
services/ingest-worker Filing ingestion, extraction, chunking, embeddings
infra/compose         Local Postgres, Qdrant, and MinIO stack
deployment/images     Dockerfiles for services
docs                  Architecture, data-source, and operating notes
```

## Data Strategy

SignalForge is SEC-first. The MVP uses official, public SEC sources before adding optional vendor or user-uploaded data.

Primary sources:

- SEC ticker mappings
- SEC submissions API
- SEC XBRL company facts API
- SEC Archives filing documents
- SEC structured disclosure RSS feeds

Optional later sources:

- Manual transcript/report uploads
- GDELT news discovery
- FRED macro data
- FMP or Quartr transcript connectors

## Development Status

This repository is being built phase by phase with clean, meaningful commits.

Current target phase:

- Repository foundation
- Local infrastructure
- FastAPI application shell
- SEC ticker and filing sync
- Initial tests and CI

## Run Locally

Fast path:

```sh
mise run up
```

Stop everything:

```sh
mise run down
```

Manual path:

Install dependencies:

```sh
uv sync --project apps/api
npm install --prefix apps/web
```

Start local infrastructure:

```sh
docker compose -f infra/compose/docker-compose.yaml up -d
```

Apply database migrations:

```sh
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head
```

Run the API:

```sh
uv run --project apps/api uvicorn signal_forge_api.main:app --reload
```

Run the dashboard:

```sh
npm run dev --prefix apps/web
```

Open the dashboard at `http://localhost:5173` and the API docs at `http://localhost:8000/docs`.

## Phase-One API

The current API supports:

```txt
GET  /health
GET  /api/v1/companies/search?q=AAPL
POST /api/v1/companies/{ticker}/sync
GET  /api/v1/companies/{ticker}
GET  /api/v1/companies/{ticker}/filings
```

The Vite dashboard uses these endpoints to search SEC company metadata, sync filing history, and display recent filings.

## License

MIT. See [LICENSE](LICENSE).
