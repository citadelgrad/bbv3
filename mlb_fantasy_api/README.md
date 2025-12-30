# MLB Fantasy API

FastAPI backend for MLB Fantasy Baseball application.

## Development

```bash
# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload
```

## Docker

```bash
# Build and run
docker compose up -d
```
