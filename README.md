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

## License

MIT. See [LICENSE](LICENSE).
