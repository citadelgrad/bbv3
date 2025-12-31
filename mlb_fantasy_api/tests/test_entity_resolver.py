"""Tests for the entity resolver service."""

import pytest

from app.models.player import Player
from app.models.player_alias import PlayerNameAlias
from app.services.entity_resolver import (
    EntityResolver,
    ResolutionContext,
    ResolutionMethod,
)


@pytest.fixture
def resolver():
    """Create an entity resolver instance."""
    return EntityResolver()


class TestResolveByMlbId:
    """Tests for resolution by MLB ID."""

    @pytest.mark.asyncio
    async def test_resolves_by_mlb_id(self, test_session, resolver):
        """Test that player is resolved by MLB ID with 100% confidence."""
        player = Player(
            full_name="Shohei Ohtani",
            name_normalized="shohei ohtani",
            first_name="Shohei",
            last_name="Ohtani",
            mlb_id=660271,
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        context = ResolutionContext(mlb_id=660271)
        result = await resolver.resolve(test_session, "Shohei Ohtani", context)

        assert result.resolved is True
        assert result.player is not None
        assert result.player.full_name == "Shohei Ohtani"
        assert result.confidence == 1.0
        assert result.method == ResolutionMethod.EXTERNAL_ID

    @pytest.mark.asyncio
    async def test_returns_unresolved_for_unknown_mlb_id(self, test_session, resolver):
        """Test that unknown MLB ID returns unresolved."""
        context = ResolutionContext(mlb_id=999999)
        result = await resolver.resolve(test_session, "Unknown Player", context)

        assert result.resolved is False
        assert result.player is None


class TestResolveByFangraphsId:
    """Tests for resolution by FanGraphs ID."""

    @pytest.mark.asyncio
    async def test_resolves_by_fangraphs_id(self, test_session, resolver):
        """Test that player is resolved by FanGraphs ID."""
        player = Player(
            full_name="Mike Trout",
            name_normalized="mike trout",
            first_name="Mike",
            last_name="Trout",
            fangraphs_id="10155",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        context = ResolutionContext(fangraphs_id="10155")
        result = await resolver.resolve(test_session, "Mike Trout", context)

        assert result.resolved is True
        assert result.player.full_name == "Mike Trout"
        assert result.confidence == 1.0
        assert result.method == ResolutionMethod.EXTERNAL_ID


class TestResolveByExactName:
    """Tests for resolution by exact name match."""

    @pytest.mark.asyncio
    async def test_resolves_unique_name(self, test_session, resolver):
        """Test that unique name is resolved with high confidence."""
        player = Player(
            full_name="Mookie Betts",
            name_normalized="mookie betts",
            first_name="Mookie",
            last_name="Betts",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        result = await resolver.resolve(test_session, "Mookie Betts")

        assert result.resolved is True
        assert result.player.full_name == "Mookie Betts"
        assert result.confidence == 0.95
        assert result.method == ResolutionMethod.EXACT_MATCH

    @pytest.mark.asyncio
    async def test_handles_case_insensitive_matching(self, test_session, resolver):
        """Test that name matching is case insensitive."""
        player = Player(
            full_name="Aaron Judge",
            name_normalized="aaron judge",
            first_name="Aaron",
            last_name="Judge",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        result = await resolver.resolve(test_session, "AARON JUDGE")

        assert result.resolved is True
        assert result.player.full_name == "Aaron Judge"


class TestWillSmithProblem:
    """Tests for the 'Will Smith Problem' - multiple players with same name."""

    @pytest.fixture
    async def will_smiths(self, test_session):
        """Create two Will Smith players."""
        catcher = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            mlb_id=669257,
            current_team_abbrev="LAD",
            primary_position="C",
            status="active",
        )
        reliever = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            mlb_id=519293,
            current_team_abbrev="TEX",
            primary_position="RP",
            status="active",
        )
        test_session.add_all([catcher, reliever])
        await test_session.commit()
        return catcher, reliever

    @pytest.mark.asyncio
    async def test_returns_candidates_for_ambiguous_name(
        self, test_session, resolver, will_smiths
    ):
        """Test that multiple candidates are returned for ambiguous name."""
        result = await resolver.resolve(test_session, "Will Smith")

        assert result.resolved is False
        assert result.player is None
        assert len(result.candidates) == 2
        assert result.requires_confirmation is True

    @pytest.mark.asyncio
    async def test_disambiguates_by_team(self, test_session, resolver, will_smiths):
        """Test that team context disambiguates Will Smith."""
        context = ResolutionContext(team="LAD")
        result = await resolver.resolve(test_session, "Will Smith", context)

        assert result.resolved is True
        assert result.player is not None
        assert result.player.current_team_abbrev == "LAD"
        assert result.player.primary_position == "C"
        assert result.confidence == 0.85
        assert result.method == ResolutionMethod.CONTEXT_MATCH

    @pytest.mark.asyncio
    async def test_disambiguates_by_position(self, test_session, resolver, will_smiths):
        """Test that position context disambiguates Will Smith."""
        context = ResolutionContext(position="RP")
        result = await resolver.resolve(test_session, "Will Smith", context)

        assert result.resolved is True
        assert result.player is not None
        assert result.player.primary_position == "RP"
        assert result.player.current_team_abbrev == "TEX"

    @pytest.mark.asyncio
    async def test_resolves_by_mlb_id_despite_ambiguous_name(
        self, test_session, resolver, will_smiths
    ):
        """Test that MLB ID takes precedence over ambiguous name."""
        context = ResolutionContext(mlb_id=669257)
        result = await resolver.resolve(test_session, "Will Smith", context)

        assert result.resolved is True
        assert result.player.mlb_id == 669257
        assert result.player.primary_position == "C"
        assert result.confidence == 1.0


class TestResolveByAlias:
    """Tests for resolution by player alias."""

    @pytest.mark.asyncio
    async def test_resolves_by_nickname(self, test_session, resolver):
        """Test that player is resolved by nickname alias."""
        player = Player(
            full_name="Shohei Ohtani",
            name_normalized="shohei ohtani",
            first_name="Shohei",
            last_name="Ohtani",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        alias = PlayerNameAlias(
            player_id=player.id,
            alias_name="Shotime",
            alias_normalized="shotime",
            alias_type="nickname",
        )
        test_session.add(alias)
        await test_session.commit()

        result = await resolver.resolve(test_session, "Shotime")

        assert result.resolved is True
        assert result.player.full_name == "Shohei Ohtani"
        assert result.confidence == 0.90
        assert result.method == ResolutionMethod.ALIAS_MATCH


class TestUnresolvedCases:
    """Tests for unresolved resolution cases."""

    @pytest.mark.asyncio
    async def test_returns_unresolved_for_unknown_name(self, test_session, resolver):
        """Test that unknown name returns unresolved."""
        result = await resolver.resolve(test_session, "Totally Unknown Player")

        assert result.resolved is False
        assert result.player is None
        assert result.candidates == []
        assert result.confidence == 0.0
        assert result.method == ResolutionMethod.UNRESOLVED

    @pytest.mark.asyncio
    async def test_returns_unresolved_for_inactive_player(self, test_session, resolver):
        """Test that inactive players are not resolved."""
        player = Player(
            full_name="Inactive Player",
            name_normalized="inactive player",
            first_name="Inactive",
            last_name="Player",
            status="active",
            is_active=False,
        )
        test_session.add(player)
        await test_session.commit()

        result = await resolver.resolve(test_session, "Inactive Player")

        assert result.resolved is False


class TestResolutionPriority:
    """Tests for resolution method priority."""

    @pytest.mark.asyncio
    async def test_mlb_id_takes_priority(self, test_session, resolver):
        """Test that MLB ID resolution takes priority over name match."""
        # Create two players, one matching name and one matching MLB ID
        player_by_name = Player(
            full_name="Target Player",
            name_normalized="target player",
            first_name="Target",
            last_name="Player",
            mlb_id=111111,
            status="active",
        )
        player_by_id = Player(
            full_name="Different Name",
            name_normalized="different name",
            first_name="Different",
            last_name="Name",
            mlb_id=222222,
            status="active",
        )
        test_session.add_all([player_by_name, player_by_id])
        await test_session.commit()

        # Provide name that matches one player, but MLB ID of another
        context = ResolutionContext(mlb_id=222222)
        result = await resolver.resolve(test_session, "Target Player", context)

        # Should resolve to the player with matching MLB ID, not the name match
        assert result.resolved is True
        assert result.player.mlb_id == 222222
        assert result.method == ResolutionMethod.EXTERNAL_ID


class TestContextFiltering:
    """Tests for context-based filtering."""

    @pytest.mark.asyncio
    async def test_team_and_position_combined(self, test_session, resolver):
        """Test that team and position context work together."""
        # Create three players with same name on different teams/positions
        player1 = Player(
            full_name="Common Name",
            name_normalized="common name",
            first_name="Common",
            last_name="Name",
            current_team_abbrev="NYY",
            primary_position="SP",
            status="active",
        )
        player2 = Player(
            full_name="Common Name",
            name_normalized="common name",
            first_name="Common",
            last_name="Name",
            current_team_abbrev="LAD",
            primary_position="SP",
            status="active",
        )
        player3 = Player(
            full_name="Common Name",
            name_normalized="common name",
            first_name="Common",
            last_name="Name",
            current_team_abbrev="LAD",
            primary_position="C",
            status="active",
        )
        test_session.add_all([player1, player2, player3])
        await test_session.commit()

        # Use both team and position to narrow down
        context = ResolutionContext(team="LAD", position="C")
        result = await resolver.resolve(test_session, "Common Name", context)

        assert result.resolved is True
        assert result.player.current_team_abbrev == "LAD"
        assert result.player.primary_position == "C"
