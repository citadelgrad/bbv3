"""Entity resolver service for player name disambiguation."""

import uuid
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.player import Player
from app.models.player_alias import PlayerNameAlias
from app.services.player_service import normalize_name


class ResolutionMethod(str, Enum):
    """Methods used to resolve player identity."""

    EXACT_MATCH = "exact_match"
    EXTERNAL_ID = "external_id"
    CONTEXT_MATCH = "context_match"
    ALIAS_MATCH = "alias_match"
    UNRESOLVED = "unresolved"


@dataclass
class ResolutionContext:
    """Context for player name resolution."""

    team: str | None = None
    position: str | None = None
    mlb_id: int | None = None
    fangraphs_id: str | None = None


@dataclass
class ResolutionResult:
    """Result of entity resolution."""

    resolved: bool
    player: Player | None
    confidence: float  # 0.0 - 1.0
    method: ResolutionMethod
    candidates: list[Player] = field(default_factory=list)
    requires_confirmation: bool = False

    @property
    def player_id(self) -> uuid.UUID | None:
        """Get the resolved player ID."""
        return self.player.id if self.player else None


class EntityResolver:
    """Service for resolving player names to canonical Player IDs.

    Implements a multi-tier resolution strategy:
    1. External ID lookup (if provided)
    2. Exact normalized name match
    3. Alias name match
    4. Context-based disambiguation (team/position)

    Does NOT use LLM disambiguation - that's for a future phase.
    """

    async def resolve(
        self,
        db: AsyncSession,
        name: str,
        context: ResolutionContext | None = None,
    ) -> ResolutionResult:
        """Resolve a player name to a canonical Player ID.

        Args:
            db: Database session.
            name: Player name to resolve.
            context: Optional context for disambiguation.

        Returns:
            Resolution result with player, confidence, and method.
        """
        context = context or ResolutionContext()

        # Tier 1: External ID lookup (instant, 100% confidence)
        if context.mlb_id:
            result = await self._resolve_by_mlb_id(db, context.mlb_id)
            if result.resolved:
                return result

        if context.fangraphs_id:
            result = await self._resolve_by_fangraphs_id(db, context.fangraphs_id)
            if result.resolved:
                return result

        # Tier 2: Exact name match
        result = await self._resolve_by_exact_name(db, name)
        if result.resolved:
            return result

        # If we have candidates from name match, try to disambiguate
        if result.candidates:
            disambiguated = await self._disambiguate_by_context(
                result.candidates,
                context,
            )
            # Return disambiguated result (whether resolved or still ambiguous)
            return disambiguated

        # Tier 3: Alias match (only if no candidates from exact name)
        result = await self._resolve_by_alias(db, name)
        if result.resolved:
            return result

        # If we have candidates from alias match, try to disambiguate
        if result.candidates:
            disambiguated = await self._disambiguate_by_context(
                result.candidates,
                context,
            )
            return disambiguated

        # No matches found
        logger.warning(
            "Entity resolution failed",
            name=name,
            context_team=context.team,
            context_position=context.position,
        )

        return ResolutionResult(
            resolved=False,
            player=None,
            confidence=0.0,
            method=ResolutionMethod.UNRESOLVED,
            candidates=[],
            requires_confirmation=False,
        )

    async def _resolve_by_mlb_id(
        self,
        db: AsyncSession,
        mlb_id: int,
    ) -> ResolutionResult:
        """Resolve by MLB ID (highest confidence)."""
        stmt = (
            select(Player)
            .where(Player.mlb_id == mlb_id)
            .where(Player.is_active.is_(True))
        )
        result = await db.execute(stmt)
        player = result.scalar_one_or_none()

        if player:
            logger.info(
                "Resolved player by MLB ID",
                mlb_id=mlb_id,
                player_id=str(player.id),
                player_name=player.full_name,
            )
            return ResolutionResult(
                resolved=True,
                player=player,
                confidence=1.0,
                method=ResolutionMethod.EXTERNAL_ID,
            )

        return ResolutionResult(
            resolved=False,
            player=None,
            confidence=0.0,
            method=ResolutionMethod.UNRESOLVED,
        )

    async def _resolve_by_fangraphs_id(
        self,
        db: AsyncSession,
        fangraphs_id: str,
    ) -> ResolutionResult:
        """Resolve by FanGraphs ID."""
        stmt = (
            select(Player)
            .where(Player.fangraphs_id == fangraphs_id)
            .where(Player.is_active.is_(True))
        )
        result = await db.execute(stmt)
        player = result.scalar_one_or_none()

        if player:
            logger.info(
                "Resolved player by FanGraphs ID",
                fangraphs_id=fangraphs_id,
                player_id=str(player.id),
                player_name=player.full_name,
            )
            return ResolutionResult(
                resolved=True,
                player=player,
                confidence=1.0,
                method=ResolutionMethod.EXTERNAL_ID,
            )

        return ResolutionResult(
            resolved=False,
            player=None,
            confidence=0.0,
            method=ResolutionMethod.UNRESOLVED,
        )

    async def _resolve_by_exact_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> ResolutionResult:
        """Resolve by exact normalized name match."""
        normalized = normalize_name(name)

        stmt = (
            select(Player)
            .where(Player.name_normalized == normalized)
            .where(Player.is_active.is_(True))
        )
        result = await db.execute(stmt)
        players = list(result.scalars().all())

        if len(players) == 1:
            logger.info(
                "Resolved player by exact name match",
                name=name,
                player_id=str(players[0].id),
            )
            return ResolutionResult(
                resolved=True,
                player=players[0],
                confidence=0.95,
                method=ResolutionMethod.EXACT_MATCH,
            )

        if len(players) > 1:
            # Multiple matches - the "Will Smith Problem"
            logger.info(
                "Multiple players match name",
                name=name,
                count=len(players),
                player_ids=[str(p.id) for p in players],
            )
            return ResolutionResult(
                resolved=False,
                player=None,
                confidence=0.0,
                method=ResolutionMethod.UNRESOLVED,
                candidates=players,
                requires_confirmation=True,
            )

        return ResolutionResult(
            resolved=False,
            player=None,
            confidence=0.0,
            method=ResolutionMethod.UNRESOLVED,
        )

    async def _resolve_by_alias(
        self,
        db: AsyncSession,
        name: str,
    ) -> ResolutionResult:
        """Resolve by alias name match."""
        normalized = normalize_name(name)

        stmt = (
            select(Player)
            .join(PlayerNameAlias)
            .where(PlayerNameAlias.alias_normalized == normalized)
            .where(Player.is_active.is_(True))
        )
        result = await db.execute(stmt)
        players = list(result.scalars().all())

        if len(players) == 1:
            logger.info(
                "Resolved player by alias",
                alias=name,
                player_id=str(players[0].id),
                player_name=players[0].full_name,
            )
            return ResolutionResult(
                resolved=True,
                player=players[0],
                confidence=0.90,
                method=ResolutionMethod.ALIAS_MATCH,
            )

        if len(players) > 1:
            return ResolutionResult(
                resolved=False,
                player=None,
                confidence=0.0,
                method=ResolutionMethod.UNRESOLVED,
                candidates=players,
                requires_confirmation=True,
            )

        return ResolutionResult(
            resolved=False,
            player=None,
            confidence=0.0,
            method=ResolutionMethod.UNRESOLVED,
        )

    async def _disambiguate_by_context(
        self,
        candidates: list[Player],
        context: ResolutionContext,
    ) -> ResolutionResult:
        """Disambiguate candidates using context (team, position)."""
        filtered = candidates.copy()

        # Filter by team
        if context.team:
            team_normalized = context.team.upper()
            team_filtered = [
                p for p in filtered
                if p.current_team_abbrev
                and p.current_team_abbrev.upper() == team_normalized
            ]
            if team_filtered:
                filtered = team_filtered

        # Filter by position
        if context.position:
            pos_normalized = context.position.upper()
            pos_filtered = [
                p for p in filtered
                if p.primary_position
                and p.primary_position.upper() == pos_normalized
            ]
            if pos_filtered:
                filtered = pos_filtered

        if len(filtered) == 1:
            logger.info(
                "Resolved player by context disambiguation",
                player_id=str(filtered[0].id),
                player_name=filtered[0].full_name,
                context_team=context.team,
                context_position=context.position,
            )
            return ResolutionResult(
                resolved=True,
                player=filtered[0],
                confidence=0.85,
                method=ResolutionMethod.CONTEXT_MATCH,
            )

        # Still ambiguous
        logger.info(
            "Context disambiguation insufficient",
            remaining_candidates=len(filtered),
            context_team=context.team,
            context_position=context.position,
        )
        return ResolutionResult(
            resolved=False,
            player=None,
            confidence=0.0,
            method=ResolutionMethod.UNRESOLVED,
            candidates=filtered,
            requires_confirmation=True,
        )


# Singleton instance
entity_resolver = EntityResolver()
