# MLB Fantasy Baseball API - Technical Specification

## Executive Summary

This document specifies the architecture and implementation requirements for the MLB Fantasy Baseball application's Python API backend. The initial phase covers the core API application structure, Supabase authentication integration, and centralized logging service.

---

## 1. Technology Stack

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| Framework | FastAPI | 0.115+ | Async support, automatic OpenAPI docs, type hints |
| Server | Uvicorn | 0.32+ | ASGI server with excellent performance |
| Database | PostgreSQL | 15+ | Robust relational DB for complex fantasy data |
| ORM | SQLAlchemy | 2.0+ | Async support, mature ecosystem |
| Auth | Supabase Auth | - | Managed auth service, handles users/tokens/OAuth |
| JWT Validation | PyJWT | 2.8+ | Validating Supabase-issued tokens |
| Validation | Pydantic | 2.0+ | Native FastAPI integration |
| Logging | structlog | 24.0+ | Structured JSON logging |
| Testing | pytest + pytest-asyncio | 8.0+ | Async test support |
| Package Manager | uv | 0.5+ | Fast, reliable Python package management |

---

## 2. Project Structure

```
mlb_fantasy_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # API v1 router aggregation
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── users.py    # User profile endpoints
│   │   │       └── health.py   # Health check endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── supabase.py         # Supabase client and JWT validation
│   │   ├── logging.py          # Centralized logging service
│   │   └── exceptions.py       # Custom exception handlers
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # SQLAlchemy base model
│   │   └── user_profile.py     # User profile model (app-specific data)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py             # User schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py     # User profile business logic
│   │
│   └── db/
│       ├── __init__.py
│       ├── session.py          # Database session management
│       └── migrations/         # Alembic migrations
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_auth.py            # Auth middleware tests
│   └── test_logging.py
│
├── alembic.ini
├── pyproject.toml              # Project config and dependencies (uv)
├── uv.lock                     # Lock file (generated)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 3. Configuration Management

### 3.1 Environment Variables

```
# Application
APP_NAME=mlb-fantasy-api
APP_ENV=development|staging|production
DEBUG=true|false
API_VERSION=v1

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database (app-specific data, not Supabase's DB)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret  # For token validation

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
LOG_FORMAT=json|console
LOG_OUTPUT=stdout|file
LOG_FILE_PATH=/var/log/mlb-fantasy/api.log
```

### 3.2 Configuration Class

The configuration system should use Pydantic's `BaseSettings` for automatic environment variable loading with validation and type coercion.

---

## 4. Authentication System (Supabase Auth)

### 4.1 Architecture Overview

Authentication is handled entirely by Supabase Auth. The client (web/mobile app) communicates directly with Supabase for all auth operations. The FastAPI backend validates Supabase-issued JWTs on protected routes.

```
┌─────────┐                              ┌─────────────┐
│  Client │ ──── Auth (signup/login) ──▶ │  Supabase   │
│  (App)  │ ◀─── JWT tokens ──────────── │    Auth     │
└────┬────┘                              └─────────────┘
     │
     │  Authorization: Bearer <supabase_jwt>
     ▼
┌─────────┐
│ FastAPI │ ──── Validates JWT using SUPABASE_JWT_SECRET
│   API   │ ──── Extracts user_id from token claims
└─────────┘
```

### 4.2 Client-Side Auth (Handled by Supabase)

The following operations happen client-side using the Supabase SDK:

- **Sign up**: `supabase.auth.signUp({ email, password })`
- **Sign in**: `supabase.auth.signInWithPassword({ email, password })`
- **Sign out**: `supabase.auth.signOut()`
- **Password reset**: `supabase.auth.resetPasswordForEmail(email)`
- **OAuth**: `supabase.auth.signInWithOAuth({ provider: 'google' })`
- **Token refresh**: Handled automatically by Supabase SDK

### 4.3 Backend JWT Validation

The FastAPI backend validates tokens and extracts user information:

```python
# core/supabase.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate Supabase JWT and return user claims."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### 4.4 Supabase JWT Structure

Supabase JWTs contain the following claims:

```json
{
  "aud": "authenticated",
  "exp": 1705314000,
  "iat": 1705312200,
  "iss": "https://your-project.supabase.co/auth/v1",
  "sub": "user-uuid",
  "email": "user@example.com",
  "phone": "",
  "app_metadata": {
    "provider": "email",
    "providers": ["email"]
  },
  "user_metadata": {
    "display_name": "Fantasy Player"
  },
  "role": "authenticated"
}
```

### 4.5 API Endpoints

#### GET /api/v1/users/me
Returns current authenticated user's profile from the app database.

**Headers:** `Authorization: Bearer <supabase_jwt>`

**Response (200):**
```json
{
  "id": "uuid",
  "supabase_user_id": "supabase-uuid",
  "username": "fantasy_player",
  "display_name": "Fantasy Player",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-20T08:15:00Z"
}
```

#### PUT /api/v1/users/me
Updates the current user's profile.

**Headers:** `Authorization: Bearer <supabase_jwt>`

**Request Body:**
```json
{
  "username": "new_username",
  "display_name": "New Display Name"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "supabase_user_id": "supabase-uuid",
  "username": "new_username",
  "display_name": "New Display Name",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-20T10:30:00Z"
}
```

### 4.6 User Profile Creation

When a user first accesses the API after signing up via Supabase, a profile record is created automatically:

```python
# services/user_service.py
async def get_or_create_profile(
    db: AsyncSession,
    supabase_user_id: str,
    email: str
) -> UserProfile:
    """Get existing profile or create one for new users."""
    profile = await db.execute(
        select(UserProfile).where(
            UserProfile.supabase_user_id == supabase_user_id
        )
    )
    profile = profile.scalar_one_or_none()

    if not profile:
        profile = UserProfile(
            supabase_user_id=supabase_user_id,
            username=email.split("@")[0],  # Default username
            display_name=None
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    return profile
```

### 4.7 Security Considerations

- JWT validation uses the `SUPABASE_JWT_SECRET` from your Supabase project settings
- Tokens are validated for expiration and audience (`authenticated`)
- Rate limiting for auth operations is handled by Supabase
- Password policies are configured in Supabase dashboard
- MFA can be enabled in Supabase without backend changes

---

## 5. Centralized Logging Service

### 5.1 Logging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │Endpoints│  │Services │  │  Auth   │  │  Middleware     │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────────┬────────┘ │
│       │            │            │                 │          │
│       └────────────┴────────────┴─────────────────┘          │
│                            │                                 │
│                    ┌───────▼───────┐                        │
│                    │   LogService  │                        │
│                    │  (structlog)  │                        │
│                    └───────┬───────┘                        │
└────────────────────────────┼────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼────┐        ┌─────▼─────┐
   │ Console │         │   File   │        │  External │
   │ Handler │         │  Handler │        │  (future) │
   └─────────┘         └──────────┘        └───────────┘
```

### 5.2 Log Format (JSON)

```json
{
  "timestamp": "2025-01-20T08:15:30.123456Z",
  "level": "INFO",
  "logger": "mlb_fantasy_api.auth",
  "message": "User login successful",
  "request_id": "req-abc123",
  "user_id": "user-uuid",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status_code": 200,
  "duration_ms": 45.2,
  "extra": {
    "username": "fantasy_player"
  }
}
```

### 5.3 LogService Interface

```python
class LogService:
    """Centralized logging service for the application."""
    
    def get_logger(self, name: str) -> BoundLogger:
        """Get a contextualized logger for a module."""
        
    def bind(self, **kwargs) -> BoundLogger:
        """Bind additional context to the logger."""
        
    def info(self, message: str, **kwargs) -> None:
        """Log at INFO level."""
        
    def warning(self, message: str, **kwargs) -> None:
        """Log at WARNING level."""
        
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log at ERROR level with optional exception info."""
        
    def debug(self, message: str, **kwargs) -> None:
        """Log at DEBUG level."""
        
    def audit(self, action: str, resource: str, **kwargs) -> None:
        """Log security/audit events."""
```

### 5.4 Log Levels and Usage

| Level | Usage | Examples |
|-------|-------|----------|
| DEBUG | Development diagnostics | Query parameters, internal state |
| INFO | Normal operations | User login, API requests, business events |
| WARNING | Recoverable issues | Rate limit approached, deprecated endpoint used |
| ERROR | Failures requiring attention | Auth failures, database errors, external API failures |
| AUDIT | Security events | Login attempts, permission changes, data access |

### 5.5 Middleware Integration

The logging middleware captures and logs:
- Request ID generation/propagation
- Request/response timing
- HTTP method, path, status code
- Client IP and user agent
- Authenticated user ID (when available)
- Request body (sanitized, configurable)
- Error details and stack traces

### 5.6 Sensitive Data Handling

Fields automatically redacted in logs:
- `password`, `passwd`, `pwd`
- `token`, `access_token`, `refresh_token`
- `secret`, `api_key`
- `ssn`, `credit_card`, `cvv`
- Custom patterns via configuration

---

## 6. Database Schema (Initial)

### 6.1 User Profiles Table

This table stores app-specific user data. Authentication data (email, password, etc.) is managed by Supabase.

```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_user_id UUID NOT NULL UNIQUE,  -- References Supabase auth.users.id
    username VARCHAR(30) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_supabase_user_id ON user_profiles(supabase_user_id);
CREATE INDEX idx_user_profiles_username ON user_profiles(username);
```

**Note:** The `supabase_user_id` corresponds to the `sub` claim in Supabase JWTs. This links app data to Supabase-managed user accounts.

---

## 7. Error Handling

### 7.1 Standard Error Response

```json
{
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": null,
    "request_id": "req-abc123"
  }
}
```

### 7.2 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_TOKEN_EXPIRED` | 401 | Supabase JWT token has expired |
| `AUTH_TOKEN_INVALID` | 401 | JWT token is malformed or invalid |
| `AUTH_UNAUTHORIZED` | 401 | Missing or invalid authorization header |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

**Note:** Authentication errors (invalid credentials, account locked, etc.) are handled by Supabase and returned directly to the client.

---

## 8. Health Check Endpoint

### GET /api/v1/health

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-20T08:15:30Z",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 2.3
    }
  }
}
```

### GET /api/v1/health/ready

Kubernetes readiness probe - returns 200 when ready to accept traffic.

### GET /api/v1/health/live

Kubernetes liveness probe - returns 200 when application is running.

---

## 9. Testing Requirements

### 9.1 Coverage Targets

- Unit tests: 90% code coverage
- Integration tests: All API endpoints
- Auth flow: Complete happy path and error scenarios

### 9.2 Test Categories

**Unit Tests:**
- Supabase JWT validation
- Input validation schemas
- Logging service functionality
- User profile service logic

**Integration Tests:**
- Protected endpoint access with valid/invalid tokens
- User profile creation on first access
- User profile update flow
- Health check endpoints

---

## 10. Implementation Priorities

### Phase 1 (Current Scope)
1. Project scaffolding with uv
2. Database setup with SQLAlchemy async
3. Supabase Auth integration (JWT validation)
4. User profile model and migrations
5. Centralized logging service
6. Health check endpoints
7. Unit and integration tests

### Phase 2 (Future)
- League management
- Team roster management
- Player database integration
- Draft system

### Phase 3 (Future)
- Live scoring integration
- Trade system
- Waiver wire
- Notifications

---

## Appendix A: Dependencies

```toml
# pyproject.toml
[project]
name = "mlb-fantasy-api"
version = "0.1.0"
description = "MLB Fantasy Baseball API"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pyjwt>=2.8.0",
    "structlog>=24.0.0",
    "python-multipart>=0.0.9",
    "httpx>=0.27.0",
    "email-validator>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
    "factory-boy>=3.3.0",
    "ruff>=0.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

### Common uv Commands

```bash
# Initialize project
uv init

# Add dependencies
uv add fastapi uvicorn

# Add dev dependencies
uv add --dev pytest ruff

# Install all dependencies
uv sync

# Run the application
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
```

---

## Appendix B: Docker Configuration

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=development
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/mlb_fantasy
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=mlb_fantasy
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**Note:** Create a `.env` file with your Supabase credentials for local development. The `docker-compose.yml` references these via environment variable substitution.