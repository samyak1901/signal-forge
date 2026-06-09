# Architecture

SignalForge is a modular research platform. The system starts as a small monorepo with clear service boundaries and grows into a polyglot showcase only when each language has a real job.

## System Shape

```txt
                       +----------------------+
                       | Vite React Dashboard |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       | FastAPI Backend      |
                       +----+------------+----+
                            |            |
                            v            v
              +-------------------+  +-------------------+
              | Postgres          |  | Ingest Worker     |
              | metadata + runs   |  | SEC/doc pipeline  |
              +-------------------+  +---------+---------+
                                              |
                         +--------------------+--------------------+
                         v                                         v
              +-------------------+                    +-------------------+
              | MinIO             |                    | Qdrant            |
              | raw artifacts     |                    | vector index      |
              +-------------------+                    +-------------------+
```

## Phase-One Services

### `apps/api`

The API owns the external product surface:

- health checks
- company search
- SEC sync requests
- company and filing reads
- OpenAPI documentation

### `services/ingest-worker`

The worker will own long-running ingestion jobs:

- filing download
- raw artifact storage
- text extraction
- section detection
- chunking
- embedding

The first implementation may run ingestion synchronously where appropriate, but the boundary remains explicit.

### `apps/web`

The frontend is a Vite React dashboard for:

- ticker search
- company pages
- filing library
- research run traces
- source-backed chat and memo views

## Storage Responsibilities

### Postgres

Postgres stores durable application state:

- companies
- filings
- documents
- chunks
- research runs
- research steps
- citations

### MinIO

MinIO stores raw and derived artifacts:

- SEC filing HTML/TXT
- uploaded PDFs/transcripts
- extracted text artifacts
- generated reports

### Qdrant

Qdrant stores embeddings and retrieval payload metadata.

## Future Services

### Rust Registry

A Rust Axum service will eventually manage artifact hashing, state transitions, and registry APIs.

### Go Gateway

A Go service will eventually handle webhook delivery, request audit, lightweight gateway behavior, and metrics.
