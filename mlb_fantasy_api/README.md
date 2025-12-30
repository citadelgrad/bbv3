# MLB Fantasy Baseball API

FastAPI backend for the MLB Fantasy Baseball application.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Podman or Docker
- Supabase project (for authentication)

## Setup

```bash
# Install dependencies
uv sync --all-extras

# Copy environment file and configure
cp .env.example .env
# Edit .env with your Supabase credentials
```

## Development

### Start Database

```bash
podman compose up db -d
```

### Run Migrations

```bash
# Generate a new migration (after model changes)
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Start API Server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

### Run Tests

```bash
uv run pytest

# With coverage
uv run pytest --cov=app

# Verbose output
uv run pytest -v
```

### Linting & Formatting

```bash
# Check for issues
uv run ruff check app tests

# Auto-fix issues
uv run ruff check --fix app tests

# Format code
uv run ruff format app tests
```

### Stop Database

```bash
podman compose down
```

## Project Structure

```
app/
├── main.py              # FastAPI application
├── config.py            # Settings (from environment)
├── dependencies.py      # Dependency injection
├── api/v1/              # API routes
├── core/                # Auth, logging, exceptions
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic
└── db/                  # Database session & migrations
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_JWT_SECRET` - JWT secret from Supabase settings
