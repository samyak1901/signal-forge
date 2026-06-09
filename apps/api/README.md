# SignalForge API

FastAPI backend for SignalForge. The first version owns company lookup, SEC sync, filing metadata, and OpenAPI endpoints.

## Development

```sh
uv sync
uv run alembic -c alembic.ini upgrade head
uv run uvicorn signal_forge_api.main:app --reload
```

From the repository root, use:

```sh
uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head
uv run --project apps/api uvicorn signal_forge_api.main:app --reload
```

## Checks

```sh
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```
