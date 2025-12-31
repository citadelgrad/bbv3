"""Tests for the player service layer."""

from datetime import date

import pytest

from app.models.player import Player
from app.models.player_alias import PlayerNameAlias
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.services import player_service


class TestNormalizeName:
    """Tests for the normalize_name function."""

    def test_normalizes_to_lowercase(self):
        """Test that names are lowercased."""
        assert player_service.normalize_name("Shohei Ohtani") == "shohei ohtani"

    def test_strips_whitespace(self):
        """Test that whitespace is trimmed."""
        assert player_service.normalize_name("  Mike Trout  ") == "mike trout"

    def test_handles_empty_string(self):
        """Test that empty strings are handled."""
        assert player_service.normalize_name("") == ""

    def test_handles_mixed_case(self):
        """Test mixed case names."""
        assert player_service.normalize_name("AARON JUDGE") == "aaron judge"


class TestCreatePlayer:
    """Tests for the create_player function."""

    @pytest.mark.asyncio
    async def test_creates_player_with_all_fields(self, test_session):
        """Test creating a player with all fields."""
        player_data = PlayerCreate(
            full_name="Shohei Ohtani",
            first_name="Shohei",
            last_name="Ohtani",
            mlb_id=660271,
            birth_date=date(1994, 7, 5),
            current_team="Los Angeles Dodgers",
            current_team_abbrev="LAD",
            primary_position="DH",
            bats="L",
            throws="R",
            status="active",
        )

        player = await player_service.create_player(test_session, player_data)

        assert player.id is not None
        assert player.full_name == "Shohei Ohtani"
        assert player.name_normalized == "shohei ohtani"
        assert player.first_name == "Shohei"
        assert player.last_name == "Ohtani"
        assert player.mlb_id == 660271
        assert player.primary_position == "DH"
        assert player.is_active is True

    @pytest.mark.asyncio
    async def test_creates_player_with_minimal_fields(self, test_session):
        """Test creating a player with minimal fields."""
        player_data = PlayerCreate(
            full_name="Test Player",
            first_name="Test",
            last_name="Player",
        )

        player = await player_service.create_player(test_session, player_data)

        assert player.id is not None
        assert player.full_name == "Test Player"
        assert player.status == "active"
        assert player.mlb_id is None


class TestGetPlayerById:
    """Tests for the get_player_by_id function."""

    @pytest.mark.asyncio
    async def test_returns_player_when_found(self, test_session):
        """Test that player is returned when found."""
        player = Player(
            full_name="Mike Trout",
            name_normalized="mike trout",
            first_name="Mike",
            last_name="Trout",
            mlb_id=545361,
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        result = await player_service.get_player_by_id(test_session, player.id)

        assert result is not None
        assert result.full_name == "Mike Trout"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, test_session):
        """Test that None is returned for non-existent player."""
        import uuid

        result = await player_service.get_player_by_id(test_session, uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_excludes_inactive_players(self, test_session):
        """Test that inactive players are excluded."""
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

        result = await player_service.get_player_by_id(test_session, player.id)

        assert result is None


class TestGetPlayerByMlbId:
    """Tests for the get_player_by_mlb_id function."""

    @pytest.mark.asyncio
    async def test_returns_player_when_found(self, test_session):
        """Test that player is returned when found by MLB ID."""
        player = Player(
            full_name="Aaron Judge",
            name_normalized="aaron judge",
            first_name="Aaron",
            last_name="Judge",
            mlb_id=592450,
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        result = await player_service.get_player_by_mlb_id(test_session, 592450)

        assert result is not None
        assert result.full_name == "Aaron Judge"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, test_session):
        """Test that None is returned for non-existent MLB ID."""
        result = await player_service.get_player_by_mlb_id(test_session, 999999)

        assert result is None


class TestGetPlayersByName:
    """Tests for the get_players_by_name function."""

    @pytest.mark.asyncio
    async def test_returns_single_player_for_unique_name(self, test_session):
        """Test that single player is returned for unique name."""
        player = Player(
            full_name="Mookie Betts",
            name_normalized="mookie betts",
            first_name="Mookie",
            last_name="Betts",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        result = await player_service.get_players_by_name(test_session, "Mookie Betts")

        assert len(result) == 1
        assert result[0].full_name == "Mookie Betts"

    @pytest.mark.asyncio
    async def test_returns_multiple_players_for_same_name(self, test_session):
        """Test the 'Will Smith Problem' - multiple players with same name."""
        # Will Smith - Catcher (LAD)
        will_smith_catcher = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            mlb_id=669257,
            current_team_abbrev="LAD",
            primary_position="C",
            status="active",
        )
        # Will Smith - Pitcher (TEX)
        will_smith_pitcher = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            mlb_id=519293,
            current_team_abbrev="TEX",
            primary_position="RP",
            status="active",
        )
        test_session.add_all([will_smith_catcher, will_smith_pitcher])
        await test_session.commit()

        result = await player_service.get_players_by_name(test_session, "Will Smith")

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_for_unknown_name(self, test_session):
        """Test that empty list is returned for unknown name."""
        result = await player_service.get_players_by_name(
            test_session, "Unknown Player"
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_finds_player_by_alias(self, test_session):
        """Test that player can be found by alias."""
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

        result = await player_service.get_players_by_name(
            test_session, "Shotime", include_aliases=True
        )

        assert len(result) == 1
        assert result[0].full_name == "Shohei Ohtani"


class TestSearchPlayers:
    """Tests for the search_players function."""

    @pytest.mark.asyncio
    async def test_finds_players_by_partial_name(self, test_session):
        """Test partial name matching."""
        player = Player(
            full_name="Ronald Acuna Jr",
            name_normalized="ronald acuna jr",
            first_name="Ronald",
            last_name="Acuna Jr",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        result = await player_service.search_players(test_session, "acuna")

        assert len(result) == 1
        assert result[0].full_name == "Ronald Acuna Jr"

    @pytest.mark.asyncio
    async def test_respects_limit(self, test_session):
        """Test that limit is respected."""
        for i in range(5):
            player = Player(
                full_name=f"Test Player {i}",
                name_normalized=f"test player {i}",
                first_name="Test",
                last_name=f"Player {i}",
                status="active",
            )
            test_session.add(player)
        await test_session.commit()

        result = await player_service.search_players(test_session, "test", limit=2)

        assert len(result) == 2


class TestListPlayers:
    """Tests for the list_players function."""

    @pytest.mark.asyncio
    async def test_returns_paginated_results(self, test_session):
        """Test pagination works correctly."""
        for i in range(5):
            player = Player(
                full_name=f"Player {i:02d}",
                name_normalized=f"player {i:02d}",
                first_name="Player",
                last_name=f"{i:02d}",
                status="active",
            )
            test_session.add(player)
        await test_session.commit()

        players, total = await player_service.list_players(
            test_session, limit=2, offset=0
        )

        assert len(players) == 2
        assert total == 5

    @pytest.mark.asyncio
    async def test_filters_by_team(self, test_session):
        """Test filtering by team."""
        lad_player = Player(
            full_name="LAD Player",
            name_normalized="lad player",
            first_name="LAD",
            last_name="Player",
            current_team_abbrev="LAD",
            status="active",
        )
        nyy_player = Player(
            full_name="NYY Player",
            name_normalized="nyy player",
            first_name="NYY",
            last_name="Player",
            current_team_abbrev="NYY",
            status="active",
        )
        test_session.add_all([lad_player, nyy_player])
        await test_session.commit()

        players, total = await player_service.list_players(test_session, team="LAD")

        assert len(players) == 1
        assert players[0].full_name == "LAD Player"

    @pytest.mark.asyncio
    async def test_filters_by_position(self, test_session):
        """Test filtering by position."""
        catcher = Player(
            full_name="Catcher Player",
            name_normalized="catcher player",
            first_name="Catcher",
            last_name="Player",
            primary_position="C",
            status="active",
        )
        pitcher = Player(
            full_name="Pitcher Player",
            name_normalized="pitcher player",
            first_name="Pitcher",
            last_name="Player",
            primary_position="SP",
            status="active",
        )
        test_session.add_all([catcher, pitcher])
        await test_session.commit()

        players, total = await player_service.list_players(test_session, position="C")

        assert len(players) == 1
        assert players[0].full_name == "Catcher Player"


class TestUpdatePlayer:
    """Tests for the update_player function."""

    @pytest.mark.asyncio
    async def test_updates_player_fields(self, test_session):
        """Test updating player fields."""
        player = Player(
            full_name="Original Name",
            name_normalized="original name",
            first_name="Original",
            last_name="Name",
            current_team_abbrev="LAD",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        update_data = PlayerUpdate(
            current_team="New York Yankees",
            current_team_abbrev="NYY",
        )

        result = await player_service.update_player(
            test_session, player.id, update_data
        )

        assert result is not None
        assert result.current_team_abbrev == "NYY"

    @pytest.mark.asyncio
    async def test_updates_name_normalized_when_name_changes(self, test_session):
        """Test that name_normalized is updated when full_name changes."""
        player = Player(
            full_name="Old Name",
            name_normalized="old name",
            first_name="Old",
            last_name="Name",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        update_data = PlayerUpdate(full_name="New Name")

        result = await player_service.update_player(
            test_session, player.id, update_data
        )

        assert result.full_name == "New Name"
        assert result.name_normalized == "new name"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_player(self, test_session):
        """Test that None is returned for non-existent player."""
        import uuid

        update_data = PlayerUpdate(current_team="Some Team")

        result = await player_service.update_player(
            test_session, uuid.uuid4(), update_data
        )

        assert result is None


class TestAddPlayerAlias:
    """Tests for the add_player_alias function."""

    @pytest.mark.asyncio
    async def test_adds_alias_to_player(self, test_session):
        """Test adding an alias to a player."""
        player = Player(
            full_name="Shohei Ohtani",
            name_normalized="shohei ohtani",
            first_name="Shohei",
            last_name="Ohtani",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        alias = await player_service.add_player_alias(
            test_session, player.id, "Shotime", "nickname"
        )

        assert alias is not None
        assert alias.alias_name == "Shotime"
        assert alias.alias_normalized == "shotime"
        assert alias.alias_type == "nickname"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_player(self, test_session):
        """Test that None is returned for non-existent player."""
        import uuid

        alias = await player_service.add_player_alias(
            test_session, uuid.uuid4(), "Some Alias", "nickname"
        )

        assert alias is None


class TestDeactivatePlayer:
    """Tests for the deactivate_player function."""

    @pytest.mark.asyncio
    async def test_deactivates_player(self, test_session):
        """Test deactivating a player."""
        player = Player(
            full_name="Active Player",
            name_normalized="active player",
            first_name="Active",
            last_name="Player",
            status="active",
            is_active=True,
        )
        test_session.add(player)
        await test_session.commit()

        result = await player_service.deactivate_player(test_session, player.id)

        assert result is True

        # Verify player is no longer findable
        found = await player_service.get_player_by_id(test_session, player.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_returns_false_for_missing_player(self, test_session):
        """Test that False is returned for non-existent player."""
        import uuid

        result = await player_service.deactivate_player(test_session, uuid.uuid4())

        assert result is False
