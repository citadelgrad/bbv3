"""Tests for scouting API endpoints."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.scouting_report import ScoutingReport


class TestResearchPlayerEndpoint:
    """Tests for POST /api/v1/scouting/research endpoint."""

    @pytest.mark.asyncio
    async def test_research_player_returns_cached_report(
        self, client: AsyncClient, test_session, valid_token
    ):
        """Test that cached reports are returned with 200 status."""
        # Create a cached report
        report = ScoutingReport(
            player_name="Shohei Ohtani",
            player_name_normalized="shohei ohtani",
            summary="Elite two-way player having MVP season",
            recent_stats="**Last 14 Days:** AVG: .320, HR: 4, OPS: 1.050",
            injury_status="Healthy",
            fantasy_outlook="Must start in all formats. Elite production.",
            detailed_analysis="Ohtani continues to dominate both on the mound and at the plate.",
            sources=[{"title": "ESPN", "uri": "https://espn.com/mlb"}],
            token_usage={
                "prompt_tokens": 1000,
                "response_tokens": 500,
                "total_tokens": 1500,
                "estimated_cost": "$0.008750",
            },
            expires_at=datetime.now(UTC) + timedelta(hours=12),
        )
        test_session.add(report)
        await test_session.commit()

        response = await client.post(
            "/api/v1/scouting/research",
            json={"player_name": "Shohei Ohtani"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cached"
        assert data["report"]["player_name"] == "Shohei Ohtani"
        assert "summary" in data["report"]

    @pytest.mark.asyncio
    async def test_research_player_triggers_job_on_cache_miss(
        self, client: AsyncClient, valid_token
    ):
        """Test that cache miss triggers a background job."""
        import httpx

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {"id": "test-job-id-123"}
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200

        # Create a mock AsyncClient that returns our mock response
        async def mock_post(*args, **kwargs):
            return mock_response

        with patch("app.api.v1.endpoints.scouting.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = mock_post
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client_instance

            response = await client.post(
                "/api/v1/scouting/research",
                json={"player_name": "Unknown Player XYZ"},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["job_id"] == "test-job-id-123"
        assert "Poll" in data["message"]

    @pytest.mark.asyncio
    async def test_research_player_requires_auth(self, client: AsyncClient):
        """Test that endpoint requires authentication."""
        response = await client.post(
            "/api/v1/scouting/research",
            json={"player_name": "Mike Trout"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_research_player_validates_player_name(
        self, client: AsyncClient, valid_token
    ):
        """Test that player name is validated."""
        # Too short
        response = await client.post(
            "/api/v1/scouting/research",
            json={"player_name": "A"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert response.status_code == 422

        # Empty
        response = await client.post(
            "/api/v1/scouting/research",
            json={"player_name": ""},
            headers={"Authorization": f"Bearer {valid_token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_research_player_handles_jobs_service_unavailable(
        self, client: AsyncClient, valid_token
    ):
        """Test graceful handling when Jobs service is unavailable."""
        import httpx

        async def mock_post(*args, **kwargs):
            raise httpx.RequestError("Connection refused")

        with patch("app.api.v1.endpoints.scouting.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.post = mock_post
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client_instance

            response = await client.post(
                "/api/v1/scouting/research",
                json={"player_name": "Aaron Judge"},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

        assert response.status_code == 503
        resp_json = response.json()
        # API uses custom error format: {"error": {"message": "..."}}
        error_message = resp_json.get("error", {}).get("message", "")
        assert "unavailable" in error_message.lower()


class TestGetJobStatusEndpoint:
    """Tests for GET /api/v1/scouting/jobs/{job_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_job_status_returns_status(
        self, client: AsyncClient, valid_token
    ):
        """Test that job status is returned correctly."""
        import httpx

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.json.return_value = {
            "id": "test-job-123",
            "status": "SUCCESS",
            "result": {"player_name": "Mike Trout"},
        }
        mock_response.raise_for_status = MagicMock()
        mock_response.status_code = 200

        async def mock_get(*args, **kwargs):
            return mock_response

        with patch("app.api.v1.endpoints.scouting.httpx.AsyncClient") as MockClient:
            mock_client_instance = AsyncMock()
            mock_client_instance.get = mock_get
            mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_instance.__aexit__ = AsyncMock(return_value=None)
            MockClient.return_value = mock_client_instance

            response = await client.get(
                "/api/v1/scouting/jobs/test-job-123",
                headers={"Authorization": f"Bearer {valid_token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_get_job_status_requires_auth(self, client: AsyncClient):
        """Test that endpoint requires authentication."""
        response = await client.get("/api/v1/scouting/jobs/test-job-123")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_job_status_handles_not_found(
        self, client: AsyncClient, valid_token
    ):
        """Test handling of non-existent job."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not found", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            response = await client.get(
                "/api/v1/scouting/jobs/non-existent-job",
                headers={"Authorization": f"Bearer {valid_token}"},
            )

        assert response.status_code == 404


class TestGetReportByPlayerEndpoint:
    """Tests for GET /api/v1/scouting/reports/{player_name} endpoint."""

    @pytest.mark.asyncio
    async def test_get_report_returns_report(
        self, client: AsyncClient, test_session, valid_token
    ):
        """Test that existing report is returned."""
        report = ScoutingReport(
            player_name="Mookie Betts",
            player_name_normalized="mookie betts",
            summary="Elite five-tool player",
            recent_stats="AVG: .290, OPS: .900",
            injury_status="Healthy",
            fantasy_outlook="Top 10 overall player",
            detailed_analysis="Betts continues to produce.",
            sources=[],
            token_usage={
                "prompt_tokens": 100,
                "response_tokens": 50,
                "total_tokens": 150,
                "estimated_cost": "$0.001",
            },
            expires_at=datetime.now(UTC) + timedelta(hours=12),
        )
        test_session.add(report)
        await test_session.commit()

        response = await client.get(
            "/api/v1/scouting/reports/Mookie Betts",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["player_name"] == "Mookie Betts"

    @pytest.mark.asyncio
    async def test_get_report_not_found(self, client: AsyncClient, valid_token):
        """Test 404 when report not found."""
        response = await client.get(
            "/api/v1/scouting/reports/NonExistent Player",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_report_excludes_expired_by_default(
        self, client: AsyncClient, test_session, valid_token
    ):
        """Test that expired reports are excluded by default."""
        report = ScoutingReport(
            player_name="Old Report Player",
            player_name_normalized="old report player",
            summary="Stale data",
            recent_stats="Old stats",
            injury_status="Unknown",
            fantasy_outlook="Outdated",
            detailed_analysis="This report is expired.",
            sources=[],
            token_usage={
                "prompt_tokens": 100,
                "response_tokens": 50,
                "total_tokens": 150,
                "estimated_cost": "$0.001",
            },
            expires_at=datetime.now(UTC) - timedelta(hours=1),  # Expired
        )
        test_session.add(report)
        await test_session.commit()

        response = await client.get(
            "/api/v1/scouting/reports/Old Report Player",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_report_includes_expired_when_requested(
        self, client: AsyncClient, test_session, valid_token
    ):
        """Test that expired reports can be included."""
        report = ScoutingReport(
            player_name="Expired Player",
            player_name_normalized="expired player",
            summary="Expired data",
            recent_stats="Old stats",
            injury_status="Unknown",
            fantasy_outlook="Stale",
            detailed_analysis="Expired report.",
            sources=[],
            token_usage={
                "prompt_tokens": 100,
                "response_tokens": 50,
                "total_tokens": 150,
                "estimated_cost": "$0.001",
            },
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        test_session.add(report)
        await test_session.commit()

        response = await client.get(
            "/api/v1/scouting/reports/Expired Player?include_expired=true",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200


class TestListReportsEndpoint:
    """Tests for GET /api/v1/scouting/reports endpoint."""

    @pytest.mark.asyncio
    async def test_list_reports_returns_empty(self, client: AsyncClient, valid_token):
        """Test that empty list is returned when no reports."""
        response = await client.get(
            "/api/v1/scouting/reports",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reports"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_reports_returns_reports(
        self, client: AsyncClient, test_session, valid_token
    ):
        """Test that reports are returned."""
        for i in range(3):
            report = ScoutingReport(
                player_name=f"Player {i}",
                player_name_normalized=f"player {i}",
                summary=f"Summary {i}",
                recent_stats=f"Stats {i}",
                injury_status="Healthy",
                fantasy_outlook=f"Outlook {i}",
                detailed_analysis=f"Analysis {i}",
                sources=[],
                token_usage={
                    "prompt_tokens": 100,
                    "response_tokens": 50,
                    "total_tokens": 150,
                    "estimated_cost": "$0.001",
                },
                expires_at=datetime.now(UTC) + timedelta(hours=12),
            )
            test_session.add(report)
        await test_session.commit()

        response = await client.get(
            "/api/v1/scouting/reports",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["reports"]) == 3
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_list_reports_pagination(
        self, client: AsyncClient, test_session, valid_token
    ):
        """Test pagination works correctly."""
        for i in range(5):
            report = ScoutingReport(
                player_name=f"Paginated Player {i}",
                player_name_normalized=f"paginated player {i}",
                summary=f"Summary {i}",
                recent_stats=f"Stats {i}",
                injury_status="Healthy",
                fantasy_outlook=f"Outlook {i}",
                detailed_analysis=f"Analysis {i}",
                sources=[],
                token_usage={
                    "prompt_tokens": 100,
                    "response_tokens": 50,
                    "total_tokens": 150,
                    "estimated_cost": "$0.001",
                },
                expires_at=datetime.now(UTC) + timedelta(hours=12),
            )
            test_session.add(report)
        await test_session.commit()

        # Get first page
        response = await client.get(
            "/api/v1/scouting/reports?limit=2&offset=0",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["reports"]) == 2
        assert data["total"] == 5

        # Get second page
        response = await client.get(
            "/api/v1/scouting/reports?limit=2&offset=2",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["reports"]) == 2

    @pytest.mark.asyncio
    async def test_list_reports_requires_auth(self, client: AsyncClient):
        """Test that endpoint requires authentication."""
        response = await client.get("/api/v1/scouting/reports")
        assert response.status_code == 401
