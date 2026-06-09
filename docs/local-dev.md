# Local Development

SignalForge uses `mise` for task orchestration, `uv` for Python packages, and Docker Compose for local infrastructure.

## Prerequisites

- Docker
- mise
- uv
- Bun

## Commands

```sh
mise install
mise run infra
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

## Environment

Configuration should be copied from `.env.example` once application services are added. Secrets must not be committed.

The SEC requires a declared `SEC_USER_AGENT`. Replace the example value with a useful project/contact string before making sustained requests.
