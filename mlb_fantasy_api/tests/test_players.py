"""Tests for the player registry API endpoints."""

import pytest

from app.models.player import Player
from app.models.player_alias import PlayerNameAlias


class TestListPlayers:
    """Tests for the GET /api/v1/players endpoint."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_players(self, client):
        """Test that empty list is returned when no players exist."""
        response = await client.get("/api/v1/players")

        assert response.status_code == 200
        data = response.json()
        assert data["players"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_returns_players_list(self, client, test_session):
        """Test that players are returned in a list."""
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

        response = await client.get("/api/v1/players")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) == 1
        assert data["players"][0]["full_name"] == "Mike Trout"
        assert data["total"] == 1

    @pytest.mark.asyncio
    async def test_filters_by_team(self, client, test_session):
        """Test filtering by team abbreviation."""
        lad_player = Player(
            full_name="Mookie Betts",
            name_normalized="mookie betts",
            first_name="Mookie",
            last_name="Betts",
            current_team_abbrev="LAD",
            status="active",
        )
        nyy_player = Player(
            full_name="Aaron Judge",
            name_normalized="aaron judge",
            first_name="Aaron",
            last_name="Judge",
            current_team_abbrev="NYY",
            status="active",
        )
        test_session.add_all([lad_player, nyy_player])
        await test_session.commit()

        response = await client.get("/api/v1/players?team=LAD")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) == 1
        assert data["players"][0]["full_name"] == "Mookie Betts"

    @pytest.mark.asyncio
    async def test_pagination(self, client, test_session):
        """Test pagination parameters."""
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

        response = await client.get("/api/v1/players?limit=2&offset=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 2


class TestSearchPlayers:
    """Tests for the GET /api/v1/players/search endpoint."""

    @pytest.mark.asyncio
    async def test_searches_by_partial_name(self, client, test_session):
        """Test searching by partial name."""
        player = Player(
            full_name="Shohei Ohtani",
            name_normalized="shohei ohtani",
            first_name="Shohei",
            last_name="Ohtani",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.get("/api/v1/players/search?q=ohtani")

        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) == 1
        assert data["players"][0]["full_name"] == "Shohei Ohtani"
        assert data["query"] == "ohtani"

    @pytest.mark.asyncio
    async def test_requires_query_parameter(self, client):
        """Test that query parameter is required."""
        response = await client.get("/api/v1/players/search")

        assert response.status_code == 422  # Validation error


class TestResolvePlayer:
    """Tests for the POST /api/v1/players/resolve endpoint."""

    @pytest.mark.asyncio
    async def test_resolves_unique_name(self, client, test_session):
        """Test resolving a unique player name."""
        player = Player(
            full_name="Ronald Acuna Jr",
            name_normalized="ronald acuna jr",
            first_name="Ronald",
            last_name="Acuna Jr",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.post(
            "/api/v1/players/resolve",
            json={"name": "Ronald Acuna Jr"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resolved"] is True
        assert data["player"]["full_name"] == "Ronald Acuna Jr"
        assert data["confidence"] == 0.95
        assert data["method"] == "exact_match"

    @pytest.mark.asyncio
    async def test_returns_candidates_for_ambiguous_name(self, client, test_session):
        """Test that candidates are returned for ambiguous name."""
        # Create two Will Smiths
        catcher = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            current_team_abbrev="LAD",
            primary_position="C",
            status="active",
        )
        reliever = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            current_team_abbrev="TEX",
            primary_position="RP",
            status="active",
        )
        test_session.add_all([catcher, reliever])
        await test_session.commit()

        response = await client.post(
            "/api/v1/players/resolve",
            json={"name": "Will Smith"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resolved"] is False
        assert len(data["candidates"]) == 2
        assert data["requires_confirmation"] is True

    @pytest.mark.asyncio
    async def test_disambiguates_with_context(self, client, test_session):
        """Test disambiguation using context."""
        # Create two Will Smiths
        catcher = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            current_team_abbrev="LAD",
            primary_position="C",
            status="active",
        )
        reliever = Player(
            full_name="Will Smith",
            name_normalized="will smith",
            first_name="Will",
            last_name="Smith",
            current_team_abbrev="TEX",
            primary_position="RP",
            status="active",
        )
        test_session.add_all([catcher, reliever])
        await test_session.commit()

        response = await client.post(
            "/api/v1/players/resolve",
            json={
                "name": "Will Smith",
                "context": {"team": "LAD"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resolved"] is True
        assert data["player"]["current_team_abbrev"] == "LAD"
        assert data["player"]["primary_position"] == "C"


class TestCreatePlayer:
    """Tests for the POST /api/v1/players endpoint."""

    @pytest.mark.asyncio
    async def test_creates_player(self, client):
        """Test creating a new player."""
        response = await client.post(
            "/api/v1/players",
            json={
                "full_name": "New Player",
                "first_name": "New",
                "last_name": "Player",
                "mlb_id": 123456,
                "primary_position": "SS",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "New Player"
        assert data["mlb_id"] == 123456
        assert data["primary_position"] == "SS"
        assert data["id"] is not None


class TestGetPlayerByMlbId:
    """Tests for the GET /api/v1/players/by-mlb-id/{mlb_id} endpoint."""

    @pytest.mark.asyncio
    async def test_returns_player_by_mlb_id(self, client, test_session):
        """Test getting player by MLB ID."""
        player = Player(
            full_name="Bryce Harper",
            name_normalized="bryce harper",
            first_name="Bryce",
            last_name="Harper",
            mlb_id=547180,
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.get("/api/v1/players/by-mlb-id/547180")

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Bryce Harper"
        assert data["mlb_id"] == 547180

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_mlb_id(self, client):
        """Test that 404 is returned for unknown MLB ID."""
        response = await client.get("/api/v1/players/by-mlb-id/999999")

        assert response.status_code == 404


class TestGetPlayer:
    """Tests for the GET /api/v1/players/{player_id} endpoint."""

    @pytest.mark.asyncio
    async def test_returns_player_by_id(self, client, test_session):
        """Test getting player by UUID."""
        player = Player(
            full_name="Freddie Freeman",
            name_normalized="freddie freeman",
            first_name="Freddie",
            last_name="Freeman",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.get(f"/api/v1/players/{player.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Freddie Freeman"

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_id(self, client):
        """Test that 404 is returned for unknown player ID."""
        import uuid

        response = await client.get(f"/api/v1/players/{uuid.uuid4()}")

        assert response.status_code == 404


class TestUpdatePlayer:
    """Tests for the PATCH /api/v1/players/{player_id} endpoint."""

    @pytest.mark.asyncio
    async def test_updates_player(self, client, test_session):
        """Test updating a player."""
        player = Player(
            full_name="Player To Update",
            name_normalized="player to update",
            first_name="Player",
            last_name="To Update",
            current_team_abbrev="LAD",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.patch(
            f"/api/v1/players/{player.id}",
            json={"current_team_abbrev": "NYY"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["current_team_abbrev"] == "NYY"


class TestDeactivatePlayer:
    """Tests for the DELETE /api/v1/players/{player_id} endpoint."""

    @pytest.mark.asyncio
    async def test_deactivates_player(self, client, test_session):
        """Test deactivating a player."""
        player = Player(
            full_name="Player To Deactivate",
            name_normalized="player to deactivate",
            first_name="Player",
            last_name="To Deactivate",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.delete(f"/api/v1/players/{player.id}")

        assert response.status_code == 204

        # Verify player is no longer returned
        get_response = await client.get(f"/api/v1/players/{player.id}")
        assert get_response.status_code == 404


class TestAddPlayerAlias:
    """Tests for the POST /api/v1/players/{player_id}/aliases endpoint."""

    @pytest.mark.asyncio
    async def test_adds_alias(self, client, test_session):
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

        response = await client.post(
            f"/api/v1/players/{player.id}/aliases",
            json={
                "player_id": str(player.id),
                "alias_name": "Shotime",
                "alias_type": "nickname",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["alias_name"] == "Shotime"
        assert data["alias_type"] == "nickname"
        assert data["alias_normalized"] == "shotime"

    @pytest.mark.asyncio
    async def test_rejects_mismatched_player_id(self, client, test_session):
        """Test that mismatched player_id is rejected."""
        import uuid

        player = Player(
            full_name="Test Player",
            name_normalized="test player",
            first_name="Test",
            last_name="Player",
            status="active",
        )
        test_session.add(player)
        await test_session.commit()

        response = await client.post(
            f"/api/v1/players/{player.id}/aliases",
            json={
                "player_id": str(uuid.uuid4()),  # Different ID
                "alias_name": "Some Alias",
                "alias_type": "nickname",
            },
        )

        assert response.status_code == 400
