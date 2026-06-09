FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY apps/api/pyproject.toml /app/apps/api/pyproject.toml
COPY apps/api/src /app/apps/api/src

RUN pip install --no-cache-dir uv \
    && uv pip install --system /app/apps/api

EXPOSE 8000

CMD ["uvicorn", "signal_forge_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
