#!/usr/bin/env python3
"""Script to populate the player registry from MLB Stats API.

Usage:
    uv run python scripts/populate_players.py

This script will:
1. Fetch all active MLB players from the MLB Stats API
2. Optionally sync 40-man rosters for all teams
3. Insert/update players in the database
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.logging import logger
from app.services.player_sync import sync_from_mlb_api, sync_team_rosters


async def main(
    include_inactive: bool = False,
    sync_rosters: bool = True,
) -> int:
    """Main entry point for player population.

    Args:
        include_inactive: Whether to include inactive players.
        sync_rosters: Whether to sync 40-man rosters.

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    logger.info(
        "Starting player population",
        database_url=settings.database_url[:50] + "...",
        include_inactive=include_inactive,
        sync_rosters=sync_rosters,
    )

    # Create database engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    total_created = 0
    total_updated = 0
    total_errors = 0

    try:
        async with async_session() as db:
            # Step 1: Sync all MLB players
            logger.info("Step 1: Syncing MLB players...")
            result = await sync_from_mlb_api(db, include_inactive=include_inactive)

            total_created += result.created
            total_updated += result.updated
            total_errors += result.errors

            logger.info(
                "MLB players sync complete",
                created=result.created,
                updated=result.updated,
                errors=result.errors,
                skipped=result.skipped,
            )

            # Step 2: Sync 40-man rosters (catches prospects not in main list)
            if sync_rosters:
                logger.info("Step 2: Syncing 40-man rosters...")
                roster_result = await sync_team_rosters(db)

                total_created += roster_result.created
                total_updated += roster_result.updated
                total_errors += roster_result.errors

                logger.info(
                    "Roster sync complete",
                    created=roster_result.created,
                    updated=roster_result.updated,
                    errors=roster_result.errors,
                )

    except Exception as e:
        logger.error("Failed to populate players", error=str(e))
        return 1
    finally:
        await engine.dispose()

    # Summary
    logger.info(
        "Player population complete",
        total_created=total_created,
        total_updated=total_updated,
        total_errors=total_errors,
    )

    print(f"\n{'='*50}")
    print("Player Population Summary")
    print(f"{'='*50}")
    print(f"Created: {total_created}")
    print(f"Updated: {total_updated}")
    print(f"Errors:  {total_errors}")
    print(f"{'='*50}\n")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Populate the player registry from MLB Stats API"
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Include inactive players in the sync",
    )
    parser.add_argument(
        "--skip-rosters",
        action="store_true",
        help="Skip syncing 40-man rosters",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without making changes",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("Dry run mode - would sync players from MLB API")
        print(f"  Include inactive: {args.include_inactive}")
        print(f"  Sync rosters: {not args.skip_rosters}")
        sys.exit(0)

    exit_code = asyncio.run(
        main(
            include_inactive=args.include_inactive,
            sync_rosters=not args.skip_rosters,
        )
    )
    sys.exit(exit_code)
