# SignalForge API

FastAPI backend for SignalForge. The first version owns company lookup, SEC sync, filing metadata, and OpenAPI endpoints.

## Development

```sh
uv sync
uv run uvicorn signal_forge_api.main:app --reload
```

## Checks

```sh
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```
