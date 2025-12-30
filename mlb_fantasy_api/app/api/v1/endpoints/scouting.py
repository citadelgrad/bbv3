"""Scouting report endpoints."""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import logger
from app.core.supabase import SupabaseUser, get_current_user
from app.db.session import get_db
from app.schemas.scouting import (
    JobStatusResponse,
    ResearchRequest,
    ResearchResponseComplete,
    ResearchResponsePending,
    ScoutingReportListResponse,
    ScoutingReportResponse,
)
from app.services import scouting_service

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.post(
    "/research",
    response_model=ResearchResponseComplete | ResearchResponsePending,
    responses={
        200: {"model": ResearchResponseComplete, "description": "Cached report found"},
        202: {"model": ResearchResponsePending, "description": "Research queued"},
    },
)
async def research_player(
    request: ResearchRequest,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research a player using Gemini Deep Research.

    If a valid cached report exists (< 24h old), returns it immediately.
    Otherwise, queues a background job and returns a job_id for polling.
    """
    player_name = request.player_name.strip()
    logger.info(
        "Research request received",
        player_name=player_name,
        user_id=str(current_user.id),
    )

    # Check cache first
    cached_report = await scouting_service.check_cache(db, player_name)
    if cached_report:
        logger.info(
            "Cache hit", player_name=player_name, report_id=str(cached_report.id)
        )
        return ResearchResponseComplete(
            status="cached",
            report=ScoutingReportResponse.model_validate(cached_report),
        )

    # Cache miss - trigger background job via Jobs API
    logger.info("Cache miss, triggering background job", player_name=player_name)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.jobs_api_url}/api/v1/jobs",
                json={
                    "task_name": "agents.research_player",
                    "args": {"player_name": player_name},
                },
                timeout=10.0,
            )
            response.raise_for_status()
            job_data = response.json()

        job_id = job_data.get("id") or job_data.get("celery_task_id")
        if not job_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to get job ID from Jobs service",
            )

        logger.info("Background job triggered", player_name=player_name, job_id=job_id)

        # Return 202 Accepted with job info
        return ResearchResponsePending(
            status="pending",
            job_id=job_id,
            message=f"Research in progress. Poll /scouting/jobs/{job_id}",
        )

    except httpx.HTTPStatusError as e:
        logger.error("Jobs API error", status_code=e.response.status_code, error=str(e))
        raise HTTPException(
            status_code=502,
            detail=f"Jobs service error: {e.response.status_code}",
        )
    except httpx.RequestError as e:
        logger.error("Jobs API connection error", error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Jobs service unavailable",
        )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: SupabaseUser = Depends(get_current_user),
):
    """Check the status of a research job."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.jobs_api_url}/api/v1/jobs/{job_id}",
                timeout=10.0,
            )
            response.raise_for_status()
            job_data = response.json()

        return JobStatusResponse(
            job_id=job_id,
            status=job_data.get("status", "unknown"),
            result=job_data.get("result"),
            error=job_data.get("error_message"),
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(
            status_code=502,
            detail=f"Jobs service error: {e.response.status_code}",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Jobs service unavailable",
        )


@router.get("/reports/{player_name}", response_model=ScoutingReportResponse)
async def get_report_by_player(
    player_name: str,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    include_expired: bool = Query(False, description="Include expired reports"),
):
    """Get a scouting report by player name."""
    report = await scouting_service.get_report_by_player_name(
        db, player_name, include_expired=include_expired
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"No report found for '{player_name}'",
        )

    return ScoutingReportResponse.model_validate(report)


@router.get("/reports", response_model=ScoutingReportListResponse)
async def list_reports(
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Maximum reports to return"),
    offset: int = Query(0, ge=0, description="Number of reports to skip"),
    include_expired: bool = Query(False, description="Include expired reports"),
):
    """List recent scouting reports."""
    reports, total = await scouting_service.get_recent_reports(
        db,
        limit=limit,
        offset=offset,
        include_expired=include_expired,
    )

    return ScoutingReportListResponse(
        reports=[ScoutingReportResponse.model_validate(r) for r in reports],
        total=total,
    )
