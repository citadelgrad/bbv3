"""Service layer for scouting report operations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.scouting_report import ScoutingReport


def normalize_player_name(name: str) -> str:
    """Normalize a player name for cache lookups."""
    return name.strip().lower()


async def get_report_by_player_name(
    db: AsyncSession,
    player_name: str,
    include_expired: bool = False,
) -> ScoutingReport | None:
    """Get a scouting report by player name.

    Args:
        db: Database session.
        player_name: The player name to look up.
        include_expired: If True, return expired reports too.

    Returns:
        The scouting report if found, None otherwise.
    """
    normalized_name = normalize_player_name(player_name)
    now = datetime.now(UTC)

    stmt = select(ScoutingReport).where(
        ScoutingReport.player_name_normalized == normalized_name
    )

    if not include_expired:
        stmt = stmt.where(ScoutingReport.expires_at > now)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_recent_reports(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    include_expired: bool = False,
) -> tuple[list[ScoutingReport], int]:
    """Get recent scouting reports.

    Args:
        db: Database session.
        limit: Maximum number of reports to return.
        offset: Number of reports to skip.
        include_expired: If True, include expired reports.

    Returns:
        Tuple of (list of reports, total count).
    """
    now = datetime.now(UTC)

    # Build base query
    base_query = select(ScoutingReport)
    if not include_expired:
        base_query = base_query.where(ScoutingReport.expires_at > now)

    # Get total count
    from sqlalchemy import func

    count_stmt = select(func.count()).select_from(
        base_query.subquery()
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get reports
    stmt = (
        base_query
        .order_by(ScoutingReport.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    reports = list(result.scalars().all())

    logger.info(
        "Retrieved scouting reports",
        count=len(reports),
        total=total,
        include_expired=include_expired,
    )

    return reports, total


async def check_cache(db: AsyncSession, player_name: str) -> ScoutingReport | None:
    """Check if a valid cached report exists for a player.

    Args:
        db: Database session.
        player_name: The player name to check.

    Returns:
        The cached report if valid, None otherwise.
    """
    return await get_report_by_player_name(db, player_name, include_expired=False)
