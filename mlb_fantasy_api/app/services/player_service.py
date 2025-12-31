"""Service layer for player registry operations."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import logger
from app.models.player import Player
from app.models.player_alias import PlayerNameAlias
from app.schemas.player import PlayerCreate, PlayerUpdate


def normalize_name(name: str) -> str:
    """Normalize a player name for consistent lookups.

    Args:
        name: The player name to normalize.

    Returns:
        Normalized name (lowercase, stripped).
    """
    return name.strip().lower()


async def create_player(
    db: AsyncSession,
    player_data: PlayerCreate,
) -> Player:
    """Create a new player in the registry.

    Args:
        db: Database session.
        player_data: Player data to create.

    Returns:
        The created player.
    """
    player = Player(
        full_name=player_data.full_name,
        name_normalized=normalize_name(player_data.full_name),
        first_name=player_data.first_name,
        last_name=player_data.last_name,
        name_suffix=player_data.name_suffix,
        mlb_id=player_data.mlb_id,
        fangraphs_id=player_data.fangraphs_id,
        baseball_reference_id=player_data.baseball_reference_id,
        birth_date=player_data.birth_date,
        current_team=player_data.current_team,
        current_team_abbrev=player_data.current_team_abbrev,
        primary_position=player_data.primary_position,
        bats=player_data.bats,
        throws=player_data.throws,
        status=player_data.status,
        mlb_org=player_data.mlb_org,
        minor_league_level=player_data.minor_league_level,
    )

    db.add(player)
    await db.commit()
    await db.refresh(player)

    logger.info(
        "Created player",
        player_id=str(player.id),
        full_name=player.full_name,
        mlb_id=player.mlb_id,
    )

    return player


async def get_player_by_id(
    db: AsyncSession,
    player_id: uuid.UUID,
) -> Player | None:
    """Get a player by their ID.

    Args:
        db: Database session.
        player_id: The player's UUID.

    Returns:
        The player if found, None otherwise.
    """
    stmt = (
        select(Player)
        .where(Player.id == player_id)
        .where(Player.is_active.is_(True))
        .options(selectinload(Player.name_aliases))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_player_by_mlb_id(
    db: AsyncSession,
    mlb_id: int,
) -> Player | None:
    """Get a player by their MLB ID.

    Args:
        db: Database session.
        mlb_id: The MLB player ID.

    Returns:
        The player if found, None otherwise.
    """
    stmt = (
        select(Player)
        .where(Player.mlb_id == mlb_id)
        .where(Player.is_active.is_(True))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_players_by_name(
    db: AsyncSession,
    name: str,
    include_aliases: bool = True,
) -> list[Player]:
    """Get players matching a normalized name.

    Args:
        db: Database session.
        name: The player name to search for.
        include_aliases: Whether to also search aliases.

    Returns:
        List of matching players.
    """
    normalized = normalize_name(name)

    # Search by main name
    stmt = (
        select(Player)
        .where(Player.name_normalized == normalized)
        .where(Player.is_active.is_(True))
    )
    result = await db.execute(stmt)
    players = list(result.scalars().all())

    if not players and include_aliases:
        # Try alias search
        stmt = (
            select(Player)
            .join(PlayerNameAlias)
            .where(PlayerNameAlias.alias_normalized == normalized)
            .where(Player.is_active.is_(True))
        )
        result = await db.execute(stmt)
        players = list(result.scalars().all())

    return players


async def search_players(
    db: AsyncSession,
    query: str,
    limit: int = 10,
) -> list[Player]:
    """Search for players by partial name match.

    Args:
        db: Database session.
        query: Search query (partial name).
        limit: Maximum results to return.

    Returns:
        List of matching players.
    """
    normalized = normalize_name(query)

    stmt = (
        select(Player)
        .where(Player.name_normalized.ilike(f"%{normalized}%"))
        .where(Player.is_active.is_(True))
        .order_by(Player.full_name)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_players(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    status: str | None = "active",
    team: str | None = None,
    position: str | None = None,
) -> tuple[list[Player], int]:
    """List players with optional filtering.

    Args:
        db: Database session.
        limit: Maximum results to return.
        offset: Number of results to skip.
        status: Filter by player status.
        team: Filter by team abbreviation.
        position: Filter by position.

    Returns:
        Tuple of (list of players, total count).
    """
    base_query = select(Player).where(Player.is_active.is_(True))

    if status:
        base_query = base_query.where(Player.status == status)
    if team:
        base_query = base_query.where(Player.current_team_abbrev == team)
    if position:
        base_query = base_query.where(Player.primary_position == position)

    # Get total count
    count_stmt = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get paginated results
    stmt = (
        base_query
        .order_by(Player.full_name)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    players = list(result.scalars().all())

    logger.info(
        "Listed players",
        count=len(players),
        total=total,
        status=status,
        team=team,
        position=position,
    )

    return players, total


async def update_player(
    db: AsyncSession,
    player_id: uuid.UUID,
    update_data: PlayerUpdate,
) -> Player | None:
    """Update a player's information.

    Args:
        db: Database session.
        player_id: The player's UUID.
        update_data: Data to update.

    Returns:
        The updated player, or None if not found.
    """
    player = await get_player_by_id(db, player_id)
    if not player:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)

    # Update name_normalized if full_name is being updated
    if "full_name" in update_dict:
        update_dict["name_normalized"] = normalize_name(update_dict["full_name"])

    for field, value in update_dict.items():
        setattr(player, field, value)

    await db.commit()
    await db.refresh(player)

    logger.info(
        "Updated player",
        player_id=str(player_id),
        fields=list(update_dict.keys()),
    )

    return player


async def add_player_alias(
    db: AsyncSession,
    player_id: uuid.UUID,
    alias_name: str,
    alias_type: str = "nickname",
) -> PlayerNameAlias | None:
    """Add an alias for a player.

    Args:
        db: Database session.
        player_id: The player's UUID.
        alias_name: The alias name.
        alias_type: Type of alias (nickname, legal_change, etc.).

    Returns:
        The created alias, or None if player not found.
    """
    player = await get_player_by_id(db, player_id)
    if not player:
        return None

    alias = PlayerNameAlias(
        player_id=player_id,
        alias_name=alias_name,
        alias_normalized=normalize_name(alias_name),
        alias_type=alias_type,
    )

    db.add(alias)
    await db.commit()
    await db.refresh(alias)

    logger.info(
        "Added player alias",
        player_id=str(player_id),
        alias_name=alias_name,
        alias_type=alias_type,
    )

    return alias


async def deactivate_player(
    db: AsyncSession,
    player_id: uuid.UUID,
) -> bool:
    """Soft delete a player by marking as inactive.

    Args:
        db: Database session.
        player_id: The player's UUID.

    Returns:
        True if player was deactivated, False if not found.
    """
    player = await get_player_by_id(db, player_id)
    if not player:
        return False

    player.is_active = False
    await db.commit()

    logger.info("Deactivated player", player_id=str(player_id))

    return True
