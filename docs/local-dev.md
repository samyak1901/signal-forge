# Local Development

SignalForge uses `mise` for task orchestration, `uv` for Python packages, and Docker Compose for local infrastructure.

## Prerequisites

- Docker
- mise
- uv
- Node.js and npm

## Commands

```sh
mise install
mise run up
mise run down
mise run infra
mise run db:migrate
mise run dev:api
mise run dev:web
mise run checks
mise run tests
```

## Local Services

The local stack will include:

- Postgres for metadata and research runs
- Qdrant for vector search
- MinIO for raw artifacts

`mise run up` starts the infrastructure, applies migrations, starts the API, and starts the Vite dashboard. It writes process IDs and logs under `.run/`.

`mise run down` stops the dashboard, stops the API, and shuts down the Docker Compose stack. Logs remain under `.run/logs/` for inspection.

## SEC Sync Smoke Test

With Postgres migrated and the API running, sync Apple filing metadata:

```sh
curl -X POST http://localhost:8000/api/v1/companies/AAPL/sync
curl http://localhost:8000/api/v1/companies/AAPL/filings
```

The dashboard performs the same flow through the Vite proxy when you search or sync a ticker from `http://localhost:5173`.

To store a raw SEC filing artifact, take one `id` from the filings response and run:

```sh
curl -X POST http://localhost:8000/api/v1/companies/AAPL/filings/{filing_id}/download
```

The API downloads the SEC primary document, stores it in MinIO under the `signal-forge` bucket, and records the object key, content type, byte size, SHA-256 hash, and download timestamp in Postgres.

## Environment

Configuration should be copied from `.env.example` once application services are added. Secrets must not be committed.

The SEC requires a declared `SEC_USER_AGENT`. Replace the example value with a useful project/contact string before making sustained requests.
