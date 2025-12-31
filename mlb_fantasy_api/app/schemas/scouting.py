"""Schemas for scouting report endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.player import EntityResolutionContext


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


class PlayerSummary(BaseModel):
    """Minimal player info for embedding in responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    current_team_abbrev: str | None
    primary_position: str | None
    mlb_id: int | None


class ScoutingReportBase(BaseModel):
    """Base schema for scouting report data."""

    summary: str = Field(..., description="Brief summary of recent performance")
    recent_stats: str = Field(..., description="Markdown formatted recent stats")
    injury_status: str = Field(..., description="Current injury status or 'Healthy'")
    fantasy_outlook: str = Field(..., description="Buy/Sell/Hold recommendation")
    detailed_analysis: str = Field(..., description="Comprehensive markdown analysis")


class ScoutingReportResponse(ScoutingReportBase):
    """Response schema for a scouting report."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    # Player identification
    player_id: uuid.UUID | None = Field(None, description="Canonical player ID")
    player: PlayerSummary | None = Field(None, description="Player details")
    player_name: str | None = Field(None, description="Player name (deprecated)")
    player_name_normalized: str | None = Field(None, description="Normalized name (deprecated)")

    # Versioning
    version: int = Field(default=1, description="Report version number")
    is_current: bool = Field(default=True, description="Whether this is the current version")
    trigger_reason: str | None = Field(None, description="Why this report was generated")

    # Metadata
    sources: list[GroundingSource]
    token_usage: TokenUsage
    created_at: datetime
    expires_at: datetime


class ResearchRequest(BaseModel):
    """Request to research a player.

    Must provide either player_id or player_name. If player_name is provided
    with an ambiguous match, context can help disambiguate.
    """

    player_id: uuid.UUID | None = Field(
        None,
        description="Canonical player ID (preferred)",
    )
    player_name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="Player name to resolve",
    )
    context: EntityResolutionContext | None = Field(
        None,
        description="Context for disambiguation (team, position, etc.)",
    )

    @model_validator(mode="after")
    def validate_player_identifier(self) -> "ResearchRequest":
        """Ensure at least one identifier is provided."""
        if not self.player_id and not self.player_name:
            raise ValueError("Either player_id or player_name is required")
        return self


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


class ResearchResponseAmbiguous(BaseModel):
    """Response when player name is ambiguous."""

    status: str = Field(default="ambiguous", description="Status of the research request")
    candidates: list[PlayerSummary] = Field(
        ...,
        description="Candidate players matching the name",
    )
    message: str = Field(
        default="Multiple players match. Please select or provide more context.",
        description="Help message for the user",
    )


class ReportVersionSummary(BaseModel):
    """Summary of a report version for history lists."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    is_current: bool
    trigger_reason: str | None
    created_at: datetime


class ReportVersionHistory(BaseModel):
    """Full version history for a player's reports."""

    player: PlayerSummary
    versions: list[ReportVersionSummary]
    total_versions: int
