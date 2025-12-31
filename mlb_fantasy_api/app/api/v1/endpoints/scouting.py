"""Scouting report endpoints."""

import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import logger
from app.core.supabase import SupabaseUser, get_current_user
from app.db.session import get_db
from app.schemas.scouting import (
    JobStatusResponse,
    PlayerSummary,
    ReportVersionHistory,
    ReportVersionSummary,
    ResearchRequest,
    ResearchResponseAmbiguous,
    ResearchResponseComplete,
    ResearchResponsePending,
    ScoutingReportListResponse,
    ScoutingReportResponse,
)
from app.services import scouting_service
from app.services.entity_resolver import ResolutionContext, entity_resolver

router = APIRouter(prefix="/scouting", tags=["scouting"])


def _build_report_response(report) -> ScoutingReportResponse:
    """Build a ScoutingReportResponse from a report model.

    Handles embedding the player summary if available.
    """
    response_data = {
        "id": report.id,
        "player_id": report.player_id,
        "player_name": report.player_name,
        "player_name_normalized": report.player_name_normalized,
        "version": report.version,
        "is_current": report.is_current,
        "trigger_reason": report.trigger_reason,
        "summary": report.summary,
        "recent_stats": report.recent_stats,
        "injury_status": report.injury_status,
        "fantasy_outlook": report.fantasy_outlook,
        "detailed_analysis": report.detailed_analysis,
        "sources": report.sources,
        "token_usage": report.token_usage,
        "created_at": report.created_at,
        "expires_at": report.expires_at,
        "player": None,
    }

    if report.player:
        response_data["player"] = PlayerSummary.model_validate(report.player)

    return ScoutingReportResponse.model_validate(response_data)


@router.post(
    "/research",
    response_model=ResearchResponseComplete | ResearchResponsePending | ResearchResponseAmbiguous,
    responses={
        200: {"model": ResearchResponseComplete, "description": "Cached report found"},
        202: {"model": ResearchResponsePending, "description": "Research queued"},
        300: {"model": ResearchResponseAmbiguous, "description": "Ambiguous player name"},
    },
)
async def research_player(
    request: ResearchRequest,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research a player using Gemini Deep Research.

    Accepts either player_id (preferred) or player_name. If player_name is
    ambiguous, returns candidates for user selection.

    If a valid cached report exists (< 24h old), returns it immediately.
    Otherwise, queues a background job and returns a job_id for polling.
    """
    player_id = request.player_id
    player_name = request.player_name.strip() if request.player_name else None

    logger.info(
        "Research request received",
        player_id=str(player_id) if player_id else None,
        player_name=player_name,
        user_id=str(current_user.id),
    )

    # If only name provided, resolve to player_id
    if not player_id and player_name:
        context = ResolutionContext(
            team=request.context.team if request.context else None,
            position=request.context.position if request.context else None,
            mlb_id=request.context.mlb_id if request.context else None,
            fangraphs_id=request.context.fangraphs_id if request.context else None,
        )
        result = await entity_resolver.resolve(db, player_name, context)

        if not result.resolved:
            if result.candidates:
                # Return 300 Multiple Choices with candidates
                logger.info(
                    "Ambiguous player name",
                    player_name=player_name,
                    candidate_count=len(result.candidates),
                )
                return JSONResponse(
                    status_code=300,
                    content=ResearchResponseAmbiguous(
                        status="ambiguous",
                        candidates=[
                            PlayerSummary.model_validate(c) for c in result.candidates
                        ],
                        message="Multiple players match. Please select or provide more context.",
                    ).model_dump(mode="json"),
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Player '{player_name}' not found in registry",
                )

        player_id = result.player_id
        player_name = result.player.full_name if result.player else player_name

    # Check cache by player_id (or fall back to name for legacy)
    cached_report = await scouting_service.check_cache(
        db,
        player_id=player_id,
        player_name=player_name,
    )
    if cached_report:
        logger.info(
            "Cache hit",
            player_id=str(player_id) if player_id else None,
            report_id=str(cached_report.id),
        )
        return ResearchResponseComplete(
            status="cached",
            report=_build_report_response(cached_report),
        )

    # Cache miss - trigger background job via Jobs API
    logger.info(
        "Cache miss, triggering background job",
        player_id=str(player_id) if player_id else None,
        player_name=player_name,
    )

    try:
        async with httpx.AsyncClient() as client:
            # Include both player_id and player_name for job
            job_args = {"player_name": player_name}
            if player_id:
                job_args["player_id"] = str(player_id)

            response = await client.post(
                f"{settings.jobs_api_url}/api/v1/jobs",
                json={
                    "task_name": "agents.research_player",
                    "args": job_args,
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

        logger.info(
            "Background job triggered",
            player_id=str(player_id) if player_id else None,
            player_name=player_name,
            job_id=job_id,
        )

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


@router.get("/reports/by-name/{player_name}", response_model=ScoutingReportResponse)
async def get_report_by_player_name(
    player_name: str,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    include_expired: bool = Query(False, description="Include expired reports"),
):
    """Get a scouting report by player name (legacy endpoint).

    Prefer using /reports/player/{player_id} for unambiguous lookups.
    """
    report = await scouting_service.get_report_by_player_name(
        db, player_name, include_expired=include_expired
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"No report found for '{player_name}'",
        )

    return _build_report_response(report)


@router.get("/reports/player/{player_id}", response_model=ScoutingReportResponse)
async def get_report_by_player_id(
    player_id: uuid.UUID,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    include_expired: bool = Query(False, description="Include expired reports"),
):
    """Get the current scouting report for a player by ID."""
    report = await scouting_service.get_current_report_by_player_id(
        db, player_id, include_expired=include_expired
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"No report found for player {player_id}",
        )

    return _build_report_response(report)


@router.get("/reports/{report_id}/history", response_model=ReportVersionHistory)
async def get_report_history(
    report_id: uuid.UUID,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a report.

    Returns all versions of reports for the same player.
    """
    # First get the report to find the player_id
    report = await scouting_service.get_report_by_id(db, report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found",
        )

    if not report.player_id:
        raise HTTPException(
            status_code=400,
            detail="Report is not linked to a player",
        )

    # Get all versions for this player
    versions, total = await scouting_service.get_report_versions(db, report.player_id)

    if not report.player:
        raise HTTPException(
            status_code=500,
            detail="Player data not found",
        )

    return ReportVersionHistory(
        player=PlayerSummary.model_validate(report.player),
        versions=[ReportVersionSummary.model_validate(v) for v in versions],
        total_versions=total,
    )


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
        reports=[_build_report_response(r) for r in reports],
        total=total,
    )
