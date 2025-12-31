"""Service layer for scouting report operations."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import logger
from app.models.player import Player
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


async def check_cache(
    db: AsyncSession,
    player_id: uuid.UUID | None = None,
    player_name: str | None = None,
) -> ScoutingReport | None:
    """Check if a valid cached report exists for a player.

    Args:
        db: Database session.
        player_id: Canonical player ID (preferred).
        player_name: Player name to look up.

    Returns:
        The cached report if valid, None otherwise.
    """
    if player_id:
        return await get_current_report_by_player_id(db, player_id)
    elif player_name:
        return await get_report_by_player_name(db, player_name, include_expired=False)
    return None


async def get_current_report_by_player_id(
    db: AsyncSession,
    player_id: uuid.UUID,
    include_expired: bool = False,
) -> ScoutingReport | None:
    """Get the current (is_current=True) report for a player by ID.

    Args:
        db: Database session.
        player_id: Canonical player UUID.
        include_expired: If True, return expired reports too.

    Returns:
        The current scouting report if found, None otherwise.
    """
    now = datetime.now(UTC)

    stmt = (
        select(ScoutingReport)
        .options(selectinload(ScoutingReport.player))
        .where(
            ScoutingReport.player_id == player_id,
            ScoutingReport.is_current.is_(True),
        )
    )

    if not include_expired:
        stmt = stmt.where(ScoutingReport.expires_at > now)

    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if report:
        logger.info(
            "Found current report by player_id",
            player_id=str(player_id),
            report_id=str(report.id),
            version=report.version,
        )

    return report


async def get_report_versions(
    db: AsyncSession,
    player_id: uuid.UUID,
) -> tuple[list[ScoutingReport], int]:
    """Get all versions of reports for a player.

    Args:
        db: Database session.
        player_id: Canonical player UUID.

    Returns:
        Tuple of (list of reports ordered by version desc, total count).
    """
    # Get count
    count_stmt = (
        select(func.count())
        .select_from(ScoutingReport)
        .where(ScoutingReport.player_id == player_id)
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get reports
    stmt = (
        select(ScoutingReport)
        .options(selectinload(ScoutingReport.player))
        .where(ScoutingReport.player_id == player_id)
        .order_by(ScoutingReport.version.desc())
    )

    result = await db.execute(stmt)
    reports = list(result.scalars().all())

    logger.info(
        "Retrieved report versions",
        player_id=str(player_id),
        total_versions=total,
    )

    return reports, total


async def get_report_by_id(
    db: AsyncSession,
    report_id: uuid.UUID,
) -> ScoutingReport | None:
    """Get a report by its ID.

    Args:
        db: Database session.
        report_id: Report UUID.

    Returns:
        The scouting report if found, None otherwise.
    """
    stmt = (
        select(ScoutingReport)
        .options(selectinload(ScoutingReport.player))
        .where(ScoutingReport.id == report_id)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_new_version(
    db: AsyncSession,
    player_id: uuid.UUID,
    report_data: dict,
    trigger_reason: str = "user_request",
) -> ScoutingReport:
    """Create a new report version for a player.

    Marks the previous current report as not current and creates
    a new report with incremented version number.

    Args:
        db: Database session.
        player_id: Canonical player UUID.
        report_data: Report content data.
        trigger_reason: Why this report was generated.

    Returns:
        The newly created scouting report.
    """
    # Find current report for this player
    current_report = await get_current_report_by_player_id(
        db, player_id, include_expired=True
    )

    new_version = 1
    previous_version_id = None

    if current_report:
        # Mark old report as not current
        current_report.is_current = False
        new_version = current_report.version + 1
        previous_version_id = current_report.id

        logger.info(
            "Marking previous report as not current",
            previous_id=str(current_report.id),
            previous_version=current_report.version,
        )

    # Create new report
    new_report = ScoutingReport(
        player_id=player_id,
        version=new_version,
        is_current=True,
        previous_version_id=previous_version_id,
        trigger_reason=trigger_reason,
        **report_data,
    )
    db.add(new_report)
    await db.flush()

    logger.info(
        "Created new report version",
        report_id=str(new_report.id),
        player_id=str(player_id),
        version=new_version,
        trigger_reason=trigger_reason,
    )

    return new_report


async def get_reports_by_player_id(
    db: AsyncSession,
    player_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    include_expired: bool = False,
    current_only: bool = True,
) -> tuple[list[ScoutingReport], int]:
    """Get reports for a player.

    Args:
        db: Database session.
        player_id: Canonical player UUID.
        limit: Maximum number of reports to return.
        offset: Number of reports to skip.
        include_expired: If True, include expired reports.
        current_only: If True, only return current versions.

    Returns:
        Tuple of (list of reports, total count).
    """
    now = datetime.now(UTC)

    # Build base conditions
    conditions = [ScoutingReport.player_id == player_id]

    if not include_expired:
        conditions.append(ScoutingReport.expires_at > now)

    if current_only:
        conditions.append(ScoutingReport.is_current.is_(True))

    # Get total count
    count_stmt = (
        select(func.count())
        .select_from(ScoutingReport)
        .where(and_(*conditions))
    )
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Get reports
    stmt = (
        select(ScoutingReport)
        .options(selectinload(ScoutingReport.player))
        .where(and_(*conditions))
        .order_by(ScoutingReport.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(stmt)
    reports = list(result.scalars().all())

    logger.info(
        "Retrieved reports by player_id",
        player_id=str(player_id),
        count=len(reports),
        total=total,
    )

    return reports, total
