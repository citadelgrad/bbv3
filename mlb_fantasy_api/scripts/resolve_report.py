#!/usr/bin/env python3
"""Manually link a scouting report to a player.

Use this for reports that couldn't be auto-resolved by the backfill script.

Usage:
    uv run python scripts/resolve_report.py <report_id> <player_id>
    uv run python scripts/resolve_report.py --list-unresolved
"""

import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.logging import logger
from app.models.player import Player
from app.models.scouting_report import ScoutingReport


async def resolve_report(
    db: AsyncSession,
    report_id: uuid.UUID,
    player_id: uuid.UUID,
) -> bool:
    """Link a report to a player.

    Args:
        db: Database session.
        report_id: Report to update.
        player_id: Player to link to.

    Returns:
        True if successful, False otherwise.
    """
    # Get the report
    stmt = select(ScoutingReport).where(ScoutingReport.id == report_id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report:
        logger.error("Report not found", report_id=str(report_id))
        return False

    # Get the player
    stmt = select(Player).where(Player.id == player_id)
    result = await db.execute(stmt)
    player = result.scalar_one_or_none()

    if not player:
        logger.error("Player not found", player_id=str(player_id))
        return False

    # Update the report
    report.player_id = player_id
    await db.commit()

    logger.info(
        "Linked report to player",
        report_id=str(report_id),
        player_id=str(player_id),
        report_player_name=report.player_name,
        player_full_name=player.full_name,
    )

    print(f"Successfully linked report to player:")
    print(f"  Report: {report.player_name} -> {player.full_name}")
    print(f"  Report ID: {report_id}")
    print(f"  Player ID: {player_id}")

    return True


async def list_unresolved(db: AsyncSession) -> list[dict]:
    """List all reports without player_id.

    Args:
        db: Database session.

    Returns:
        List of unresolved reports.
    """
    stmt = select(ScoutingReport).where(
        ScoutingReport.player_id.is_(None),
        ScoutingReport.player_name.isnot(None),
    )
    result = await db.execute(stmt)
    reports = list(result.scalars().all())

    unresolved = []
    for report in reports:
        unresolved.append({
            "report_id": str(report.id),
            "player_name": report.player_name,
            "created_at": report.created_at.isoformat(),
        })

    return unresolved


async def main(
    report_id: uuid.UUID | None = None,
    player_id: uuid.UUID | None = None,
    list_only: bool = False,
) -> int:
    """Main entry point.

    Args:
        report_id: Report to update.
        player_id: Player to link to.
        list_only: If True, just list unresolved reports.

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    # Create database engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with async_session() as db:
            if list_only:
                unresolved = await list_unresolved(db)
                if unresolved:
                    print(f"\nUnresolved Reports ({len(unresolved)}):")
                    print("-" * 60)
                    for item in unresolved:
                        print(f"  {item['report_id']}")
                        print(f"    Player: {item['player_name']}")
                        print(f"    Created: {item['created_at']}")
                        print()
                else:
                    print("\nNo unresolved reports found.")
                return 0

            if report_id and player_id:
                success = await resolve_report(db, report_id, player_id)
                return 0 if success else 1

    except Exception as e:
        logger.error("Operation failed", error=str(e))
        return 1
    finally:
        await engine.dispose()

    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manually link a scouting report to a player"
    )
    parser.add_argument(
        "report_id",
        nargs="?",
        type=str,
        help="UUID of the report to update",
    )
    parser.add_argument(
        "player_id",
        nargs="?",
        type=str,
        help="UUID of the player to link to",
    )
    parser.add_argument(
        "--list-unresolved",
        action="store_true",
        help="List all unresolved reports",
    )

    args = parser.parse_args()

    if args.list_unresolved:
        exit_code = asyncio.run(main(list_only=True))
    elif args.report_id and args.player_id:
        try:
            report_uuid = uuid.UUID(args.report_id)
            player_uuid = uuid.UUID(args.player_id)
        except ValueError as e:
            print(f"Invalid UUID: {e}")
            sys.exit(1)
        exit_code = asyncio.run(main(report_uuid, player_uuid))
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(exit_code)
