import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


class HealthCheckResult(BaseModel):
    """Individual health check result."""

    status: str
    latency_ms: float | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: str
    checks: dict[str, HealthCheckResult]


class ReadyResponse(BaseModel):
    """Readiness probe response."""

    ready: bool


class LiveResponse(BaseModel):
    """Liveness probe response."""

    alive: bool


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check the health of the application and its dependencies."""
    checks: dict[str, HealthCheckResult] = {}

    # Check database connection
    try:
        start = time.perf_counter()
        await db.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        checks["database"] = HealthCheckResult(
            status="healthy", latency_ms=round(latency, 2)
        )
    except Exception:
        checks["database"] = HealthCheckResult(status="unhealthy")

    # Determine overall status
    all_healthy = all(c.status == "healthy" for c in checks.values())
    overall_status = "healthy" if all_healthy else "unhealthy"

    return HealthResponse(
        status=overall_status,
        version=settings.api_version,
        timestamp=datetime.now(UTC).isoformat(),
        checks=checks,
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_probe(db: AsyncSession = Depends(get_db)) -> ReadyResponse:
    """Kubernetes readiness probe.

    Returns 200 when the application is ready to accept traffic.
    """
    try:
        await db.execute(text("SELECT 1"))
        return ReadyResponse(ready=True)
    except Exception:
        return ReadyResponse(ready=False)


@router.get("/live", response_model=LiveResponse)
async def liveness_probe() -> LiveResponse:
    """Kubernetes liveness probe.

    Returns 200 when the application is running.
    """
    return LiveResponse(alive=True)
