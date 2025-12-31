"""Service for syncing player data from MLB Stats API."""

from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.player import Player
from app.services.player_service import normalize_name

# MLB Stats API base URL
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"


@dataclass
class SyncResult:
    """Result of a player sync operation."""

    created: int = 0
    updated: int = 0
    errors: int = 0
    skipped: int = 0

    @property
    def total_processed(self) -> int:
        return self.created + self.updated + self.errors + self.skipped


def parse_mlb_player(player_data: dict) -> dict:
    """Parse MLB API player data into our schema.

    Args:
        player_data: Raw player data from MLB API.

    Returns:
        Dict with player fields for our schema.
    """
    # Extract name parts
    full_name = player_data.get("fullName", "")
    first_name = player_data.get("firstName", "")
    last_name = player_data.get("lastName", "")
    name_suffix = player_data.get("nameSuffix", None)

    # Get current team info
    current_team = None
    current_team_abbrev = None
    if "currentTeam" in player_data:
        current_team = player_data["currentTeam"].get("name")
        current_team_abbrev = player_data["currentTeam"].get("abbreviation")

    # Get position
    primary_position = None
    if "primaryPosition" in player_data:
        primary_position = player_data["primaryPosition"].get("abbreviation")

    # Parse birth date
    birth_date = None
    if "birthDate" in player_data:
        try:
            birth_date = datetime.strptime(
                player_data["birthDate"], "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            pass

    # Determine status
    status = "active"
    if player_data.get("active") is False:
        status = "inactive"

    return {
        "mlb_id": player_data.get("id"),
        "full_name": full_name,
        "name_normalized": normalize_name(full_name),
        "first_name": first_name,
        "last_name": last_name,
        "name_suffix": name_suffix,
        "birth_date": birth_date,
        "current_team": current_team,
        "current_team_abbrev": current_team_abbrev,
        "primary_position": primary_position,
        "bats": player_data.get("batSide", {}).get("code"),
        "throws": player_data.get("pitchHand", {}).get("code"),
        "status": status,
        "data_source": "mlb_api",
        "last_synced_at": datetime.now(UTC),
    }


async def fetch_mlb_players(
    client: httpx.AsyncClient,
    sport_id: int = 1,  # 1 = MLB
) -> list[dict]:
    """Fetch all players from MLB Stats API.

    Args:
        client: HTTP client instance.
        sport_id: Sport ID (1 = MLB).

    Returns:
        List of player dictionaries.
    """
    url = f"{MLB_API_BASE}/sports/{sport_id}/players"
    params = {
        "season": datetime.now().year,
        "hydrate": "currentTeam",
    }

    logger.info("Fetching players from MLB API", url=url, season=params["season"])

    response = await client.get(url, params=params, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    players = data.get("people", [])

    logger.info("Fetched players from MLB API", count=len(players))

    return players


async def fetch_team_roster(
    client: httpx.AsyncClient,
    team_id: int,
    roster_type: str = "40Man",
) -> list[dict]:
    """Fetch a team's roster from MLB Stats API.

    Args:
        client: HTTP client instance.
        team_id: MLB team ID.
        roster_type: Type of roster (40Man, fullRoster, etc.).

    Returns:
        List of player dictionaries.
    """
    url = f"{MLB_API_BASE}/teams/{team_id}/roster"
    params = {
        "rosterType": roster_type,
        "hydrate": "person(currentTeam)",
    }

    response = await client.get(url, params=params, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    roster = data.get("roster", [])

    # Extract player info from roster entries
    players = [entry.get("person", {}) for entry in roster if "person" in entry]

    return players


async def sync_player(
    db: AsyncSession,
    player_data: dict,
) -> tuple[Player | None, str]:
    """Sync a single player to the database.

    Args:
        db: Database session.
        player_data: Parsed player data dictionary.

    Returns:
        Tuple of (Player instance or None, action taken).
    """
    mlb_id = player_data.get("mlb_id")
    if not mlb_id:
        return None, "skipped"

    # Check if player exists
    stmt = select(Player).where(Player.mlb_id == mlb_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing player
        for field, value in player_data.items():
            if value is not None and field != "mlb_id":
                setattr(existing, field, value)
        return existing, "updated"
    else:
        # Create new player
        player = Player(**player_data)
        db.add(player)
        return player, "created"


async def sync_from_mlb_api(
    db: AsyncSession,
    include_inactive: bool = False,
) -> SyncResult:
    """Sync all MLB players from the MLB Stats API.

    Args:
        db: Database session.
        include_inactive: Whether to include inactive players.

    Returns:
        SyncResult with counts of created, updated, errors, skipped.
    """
    result = SyncResult()

    async with httpx.AsyncClient() as client:
        try:
            raw_players = await fetch_mlb_players(client)
        except httpx.HTTPError as e:
            logger.error("Failed to fetch MLB players", error=str(e))
            result.errors = 1
            return result

        for raw_player in raw_players:
            try:
                # Skip inactive if not requested
                if not include_inactive and raw_player.get("active") is False:
                    result.skipped += 1
                    continue

                player_data = parse_mlb_player(raw_player)
                player, action = await sync_player(db, player_data)

                if action == "created":
                    result.created += 1
                elif action == "updated":
                    result.updated += 1
                else:
                    result.skipped += 1

            except Exception as e:
                logger.error(
                    "Failed to sync player",
                    mlb_id=raw_player.get("id"),
                    full_name=raw_player.get("fullName"),
                    error=str(e),
                )
                result.errors += 1

        await db.commit()

    logger.info(
        "Completed MLB player sync",
        created=result.created,
        updated=result.updated,
        errors=result.errors,
        skipped=result.skipped,
    )

    return result


async def sync_team_rosters(
    db: AsyncSession,
    team_ids: list[int] | None = None,
) -> SyncResult:
    """Sync 40-man rosters for specified teams.

    Args:
        db: Database session.
        team_ids: List of MLB team IDs. If None, syncs all 30 teams.

    Returns:
        SyncResult with counts.
    """
    # All 30 MLB team IDs
    all_team_ids = [
        108,  # LAA
        109,  # ARI
        110,  # BAL
        111,  # BOS
        112,  # CHC
        113,  # CIN
        114,  # CLE
        115,  # COL
        116,  # DET
        117,  # HOU
        118,  # KC
        119,  # LAD
        120,  # WSH
        121,  # NYM
        133,  # OAK
        134,  # PIT
        135,  # SD
        136,  # SEA
        137,  # SF
        138,  # STL
        139,  # TB
        140,  # TEX
        141,  # TOR
        142,  # MIN
        143,  # PHI
        144,  # ATL
        145,  # CWS
        146,  # MIA
        147,  # NYY
        158,  # MIL
    ]

    team_ids = team_ids or all_team_ids
    result = SyncResult()

    async with httpx.AsyncClient() as client:
        for team_id in team_ids:
            try:
                raw_players = await fetch_team_roster(client, team_id)

                for raw_player in raw_players:
                    try:
                        player_data = parse_mlb_player(raw_player)
                        player, action = await sync_player(db, player_data)

                        if action == "created":
                            result.created += 1
                        elif action == "updated":
                            result.updated += 1
                        else:
                            result.skipped += 1

                    except Exception as e:
                        logger.error(
                            "Failed to sync roster player",
                            team_id=team_id,
                            mlb_id=raw_player.get("id"),
                            error=str(e),
                        )
                        result.errors += 1

            except httpx.HTTPError as e:
                logger.error(
                    "Failed to fetch team roster",
                    team_id=team_id,
                    error=str(e),
                )
                result.errors += 1

        await db.commit()

    logger.info(
        "Completed team roster sync",
        teams=len(team_ids),
        created=result.created,
        updated=result.updated,
        errors=result.errors,
    )

    return result
