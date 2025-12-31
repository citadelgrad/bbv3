#!/usr/bin/env python3
"""Backfill player_id for existing scouting reports.

This script resolves player_name → player_id for existing scouting reports
using the EntityResolver. Unresolved reports are logged for manual review.

Usage:
    uv run python scripts/backfill_player_ids.py [--dry-run]
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.logging import logger
from app.models.scouting_report import ScoutingReport
from app.services.entity_resolver import entity_resolver


async def backfill_reports(
    db: AsyncSession,
    dry_run: bool = False,
) -> tuple[int, int, list[dict]]:
    """Backfill player_id for reports that only have player_name.

    Args:
        db: Database session.
        dry_run: If True, don't make changes.

    Returns:
        Tuple of (resolved_count, skipped_count, unresolved_list).
    """
    # Get reports without player_id
    stmt = select(ScoutingReport).where(
        ScoutingReport.player_id.is_(None),
        ScoutingReport.player_name.isnot(None),
    )
    result = await db.execute(stmt)
    reports = list(result.scalars().all())

    logger.info(
        "Found reports to backfill",
        count=len(reports),
        dry_run=dry_run,
    )

    resolved = 0
    skipped = 0
    unresolved = []

    for report in reports:
        try:
            resolution = await entity_resolver.resolve(
                db,
                report.player_name,
                context=None,  # No context available from old data
            )

            if resolution.resolved:
                if not dry_run:
                    report.player_id = resolution.player_id
                resolved += 1
                logger.info(
                    "Resolved report",
                    report_id=str(report.id),
                    player_name=report.player_name,
                    player_id=str(resolution.player_id),
                    resolved_name=resolution.player.full_name if resolution.player else None,
                )
            else:
                unresolved.append({
                    "report_id": str(report.id),
                    "player_name": report.player_name,
                    "candidate_count": len(resolution.candidates),
                    "candidates": [
                        {
                            "id": str(c.id),
                            "full_name": c.full_name,
                            "team": c.current_team_abbrev,
                            "position": c.primary_position,
                        }
                        for c in resolution.candidates
                    ],
                })
                logger.warning(
                    "Failed to resolve report",
                    report_id=str(report.id),
                    player_name=report.player_name,
                    candidate_count=len(resolution.candidates),
                )

        except Exception as e:
            logger.error(
                "Error processing report",
                report_id=str(report.id),
                player_name=report.player_name,
                error=str(e),
            )
            unresolved.append({
                "report_id": str(report.id),
                "player_name": report.player_name,
                "error": str(e),
            })

    if not dry_run:
        await db.commit()

    return resolved, skipped, unresolved


async def main(dry_run: bool = False) -> int:
    """Main entry point.

    Args:
        dry_run: If True, don't make changes.

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    logger.info(
        "Starting player_id backfill",
        database_url=settings.database_url[:50] + "...",
        dry_run=dry_run,
    )

    # Create database engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    try:
        async with async_session() as db:
            resolved, skipped, unresolved = await backfill_reports(db, dry_run)

    except Exception as e:
        logger.error("Backfill failed", error=str(e))
        return 1
    finally:
        await engine.dispose()

    # Write unresolved to JSON for manual review
    if unresolved:
        output_path = Path("unresolved_reports.json")
        with open(output_path, "w") as f:
            json.dump(unresolved, f, indent=2)
        logger.info(
            "Wrote unresolved reports",
            path=str(output_path),
            count=len(unresolved),
        )

    # Summary
    logger.info(
        "Backfill complete",
        resolved=resolved,
        unresolved=len(unresolved),
        dry_run=dry_run,
    )

    print(f"\n{'='*50}")
    print("Backfill Summary")
    print(f"{'='*50}")
    print(f"Resolved:   {resolved}")
    print(f"Unresolved: {len(unresolved)}")
    if dry_run:
        print("(DRY RUN - no changes made)")
    if unresolved:
        print(f"\nUnresolved reports written to: unresolved_reports.json")
    print(f"{'='*50}\n")

    return 0 if len(unresolved) == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill player_id for existing scouting reports"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making changes",
    )

    args = parser.parse_args()

    exit_code = asyncio.run(main(dry_run=args.dry_run))
    sys.exit(exit_code)
