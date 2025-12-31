"""Pydantic schemas for player registry."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PlayerBase(BaseModel):
    """Base schema for player data."""

    full_name: str = Field(..., min_length=2, max_length=150)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    name_suffix: str | None = Field(None, max_length=10)


class PlayerCreate(PlayerBase):
    """Schema for creating a player."""

    mlb_id: int | None = None
    fangraphs_id: str | None = None
    baseball_reference_id: str | None = None
    birth_date: date | None = None
    current_team: str | None = None
    current_team_abbrev: str | None = Field(None, max_length=5)
    primary_position: str | None = Field(None, max_length=10)
    bats: str | None = Field(None, max_length=1)
    throws: str | None = Field(None, max_length=1)
    status: str = Field(default="active", max_length=20)
    mlb_org: str | None = None
    minor_league_level: str | None = None


class PlayerUpdate(BaseModel):
    """Schema for updating a player."""

    full_name: str | None = Field(None, min_length=2, max_length=150)
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    name_suffix: str | None = Field(None, max_length=10)
    current_team: str | None = None
    current_team_abbrev: str | None = Field(None, max_length=5)
    primary_position: str | None = Field(None, max_length=10)
    bats: str | None = Field(None, max_length=1)
    throws: str | None = Field(None, max_length=1)
    status: str | None = Field(None, max_length=20)
    mlb_org: str | None = None
    minor_league_level: str | None = None
    yahoo_fantasy_id: str | None = None
    espn_fantasy_id: str | None = None


class PlayerResponse(PlayerBase):
    """Schema for player responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name_normalized: str
    mlb_id: int | None
    fangraphs_id: str | None
    baseball_reference_id: str | None
    yahoo_fantasy_id: str | None
    espn_fantasy_id: str | None
    birth_date: date | None
    current_team: str | None
    current_team_abbrev: str | None
    primary_position: str | None
    bats: str | None
    throws: str | None
    status: str
    mlb_org: str | None
    minor_league_level: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PlayerListResponse(BaseModel):
    """Schema for paginated player list."""

    players: list[PlayerResponse]
    total: int
    limit: int
    offset: int


class PlayerSearchResponse(BaseModel):
    """Schema for player search results."""

    players: list[PlayerResponse]
    query: str
    total: int


class PlayerNameAliasBase(BaseModel):
    """Base schema for player name alias."""

    alias_name: str = Field(..., min_length=2, max_length=150)
    alias_type: str = Field(default="nickname", max_length=20)


class PlayerNameAliasCreate(PlayerNameAliasBase):
    """Schema for creating a player name alias."""

    player_id: uuid.UUID


class PlayerNameAliasResponse(PlayerNameAliasBase):
    """Schema for player name alias responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    player_id: uuid.UUID
    alias_normalized: str
    created_at: datetime


# Entity Resolution Schemas


class EntityResolutionContext(BaseModel):
    """Context for entity resolution."""

    team: str | None = Field(None, description="Team name or abbreviation")
    position: str | None = Field(None, description="Player position")
    date_context: date | None = Field(None, description="Date for historical context")
    mlb_id: int | None = Field(None, description="MLB ID if known")
    fangraphs_id: str | None = Field(None, description="FanGraphs ID if known")


class EntityResolutionRequest(BaseModel):
    """Request for entity resolution."""

    name: str = Field(..., min_length=2, max_length=150)
    context: EntityResolutionContext | None = None


class EntityResolutionResponse(BaseModel):
    """Response from entity resolution."""

    resolved: bool = Field(..., description="Whether resolution was successful")
    player_id: uuid.UUID | None = Field(None, description="Resolved player ID")
    player: PlayerResponse | None = Field(None, description="Resolved player details")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    method: str = Field(..., description="Resolution method used")
    candidates: list[PlayerResponse] = Field(
        default_factory=list,
        description="Candidate players if ambiguous",
    )
    requires_confirmation: bool = Field(
        False,
        description="Whether user confirmation is needed",
    )
