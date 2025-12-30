"""Schemas for scouting report endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GroundingSource(BaseModel):
    """A source used in grounding the research response."""

    title: str
    uri: str


class TokenUsage(BaseModel):
    """Token usage and cost information."""

    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    estimated_cost: str


class ScoutingReportBase(BaseModel):
    """Base schema for scouting report data."""

    player_name: str = Field(..., description="The full name of the player")
    summary: str = Field(..., description="Brief summary of recent performance")
    recent_stats: str = Field(..., description="Markdown formatted recent stats")
    injury_status: str = Field(..., description="Current injury status or 'Healthy'")
    fantasy_outlook: str = Field(..., description="Buy/Sell/Hold recommendation")
    detailed_analysis: str = Field(..., description="Comprehensive markdown analysis")


class ScoutingReportResponse(ScoutingReportBase):
    """Response schema for a scouting report."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_name_normalized: str
    sources: list[GroundingSource]
    token_usage: TokenUsage
    created_at: datetime
    expires_at: datetime


class ResearchRequest(BaseModel):
    """Request to research a player."""

    player_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="The name of the player to research",
    )


class ResearchResponsePending(BaseModel):
    """Response when research is queued."""

    status: str = Field(default="pending", description="Status of the research request")
    job_id: str = Field(..., description="Celery task ID for polling")
    message: str = Field(..., description="Status message")


class ResearchResponseComplete(BaseModel):
    """Response when research is complete (cached or generated)."""

    status: str = Field(..., description="'cached' or 'generated'")
    report: ScoutingReportResponse


class JobStatusResponse(BaseModel):
    """Response for job status check."""

    job_id: str
    status: str = Field(..., description="'pending', 'running', 'success', or 'failed'")
    result: dict | None = Field(default=None, description="Job result if complete")
    error: str | None = Field(default=None, description="Error message if failed")


class ScoutingReportListResponse(BaseModel):
    """Response for listing scouting reports."""

    reports: list[ScoutingReportResponse]
    total: int
