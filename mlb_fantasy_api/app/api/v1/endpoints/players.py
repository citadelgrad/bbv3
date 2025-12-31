"""Player registry API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.player import (
    EntityResolutionRequest,
    EntityResolutionResponse,
    PlayerCreate,
    PlayerListResponse,
    PlayerNameAliasCreate,
    PlayerNameAliasResponse,
    PlayerResponse,
    PlayerSearchResponse,
    PlayerUpdate,
)
from app.services import player_service
from app.services.entity_resolver import ResolutionContext, entity_resolver

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=PlayerListResponse)
async def list_players(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: str | None = Query("active", description="Filter by player status"),
    team: str | None = Query(None, description="Filter by team abbreviation"),
    position: str | None = Query(None, description="Filter by position"),
    db: AsyncSession = Depends(get_db),
) -> PlayerListResponse:
    """List players with optional filtering.

    Returns a paginated list of players, filtered by status, team, and/or position.
    """
    players, total = await player_service.list_players(
        db,
        limit=limit,
        offset=offset,
        status=status,
        team=team,
        position=position,
    )

    return PlayerListResponse(
        players=[PlayerResponse.model_validate(p) for p in players],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=PlayerSearchResponse)
async def search_players(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> PlayerSearchResponse:
    """Search for players by name.

    Performs a partial match search on player names.
    """
    players = await player_service.search_players(db, q, limit=limit)

    return PlayerSearchResponse(
        players=[PlayerResponse.model_validate(p) for p in players],
        query=q,
        total=len(players),
    )


@router.post("/resolve", response_model=EntityResolutionResponse)
async def resolve_player(
    request: EntityResolutionRequest,
    db: AsyncSession = Depends(get_db),
) -> EntityResolutionResponse:
    """Resolve a player name to a canonical Player ID.

    Attempts to resolve the given name to a single player using:
    1. External ID lookup (if provided in context)
    2. Exact name match
    3. Alias name match
    4. Context-based disambiguation (team/position)

    If multiple candidates exist and cannot be disambiguated,
    returns the list of candidates for user selection.
    """
    context = None
    if request.context:
        context = ResolutionContext(
            team=request.context.team,
            position=request.context.position,
            mlb_id=request.context.mlb_id,
            fangraphs_id=request.context.fangraphs_id,
        )

    result = await entity_resolver.resolve(db, request.name, context)

    return EntityResolutionResponse(
        resolved=result.resolved,
        player_id=result.player_id,
        player=PlayerResponse.model_validate(result.player) if result.player else None,
        confidence=result.confidence,
        method=result.method.value,
        candidates=[PlayerResponse.model_validate(p) for p in result.candidates],
        requires_confirmation=result.requires_confirmation,
    )


@router.post("", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    player_data: PlayerCreate,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Create a new player in the registry.

    This endpoint is primarily for administrative use or data sync.
    """
    player = await player_service.create_player(db, player_data)
    return PlayerResponse.model_validate(player)


@router.get("/by-mlb-id/{mlb_id}", response_model=PlayerResponse)
async def get_player_by_mlb_id(
    mlb_id: int,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Get a player by their MLB ID."""
    player = await player_service.get_player_by_mlb_id(db, mlb_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player with MLB ID {mlb_id} not found",
        )
    return PlayerResponse.model_validate(player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Get a player by their UUID."""
    player = await player_service.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return PlayerResponse.model_validate(player)


@router.patch("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: uuid.UUID,
    update_data: PlayerUpdate,
    db: AsyncSession = Depends(get_db),
) -> PlayerResponse:
    """Update a player's information."""
    player = await player_service.update_player(db, player_id, update_data)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return PlayerResponse.model_validate(player)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_player(
    player_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deactivate a player (soft delete)."""
    success = await player_service.deactivate_player(db, player_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )


@router.post(
    "/{player_id}/aliases",
    response_model=PlayerNameAliasResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_player_alias(
    player_id: uuid.UUID,
    alias_data: PlayerNameAliasCreate,
    db: AsyncSession = Depends(get_db),
) -> PlayerNameAliasResponse:
    """Add an alias for a player."""
    if alias_data.player_id != player_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player ID in path must match player_id in body",
        )

    alias = await player_service.add_player_alias(
        db,
        player_id,
        alias_data.alias_name,
        alias_data.alias_type,
    )
    if not alias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player {player_id} not found",
        )
    return PlayerNameAliasResponse.model_validate(alias)
