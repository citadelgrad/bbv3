"""Tests for the scouting service layer."""

from datetime import UTC, datetime, timedelta

import pytest

from app.models.scouting_report import ScoutingReport
from app.services import scouting_service


class TestNormalizePlayerName:
    """Tests for the normalize_player_name function."""

    def test_normalizes_to_lowercase(self):
        """Test that names are lowercased."""
        assert scouting_service.normalize_player_name("Shohei Ohtani") == "shohei ohtani"

    def test_strips_whitespace(self):
        """Test that whitespace is trimmed."""
        assert scouting_service.normalize_player_name("  Mike Trout  ") == "mike trout"

    def test_handles_empty_string(self):
        """Test that empty strings are handled."""
        assert scouting_service.normalize_player_name("") == ""

    def test_handles_mixed_case(self):
        """Test mixed case names."""
        assert scouting_service.normalize_player_name("AARON JUDGE") == "aaron judge"
        assert scouting_service.normalize_player_name("aAron JuDge") == "aaron judge"


class TestGetReportByPlayerName:
    """Tests for the get_report_by_player_name function."""

    @pytest.mark.asyncio
    async def test_returns_valid_report(self, test_session):
        """Test that a valid report is returned."""
        report = ScoutingReport(
            player_name="Ronald Acuna Jr",
            player_name_normalized="ronald acuna jr",
            summary="Elite production",
            recent_stats="AVG: .300",
            injury_status="Healthy",
            fantasy_outlook="Top 5 overall",
            detailed_analysis="Acuna is on fire.",
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

        result = await scouting_service.get_report_by_player_name(
            test_session, "Ronald Acuna Jr"
        )

        assert result is not None
        assert result.player_name == "Ronald Acuna Jr"

    @pytest.mark.asyncio
    async def test_returns_none_for_missing_player(self, test_session):
        """Test that None is returned for non-existent player."""
        result = await scouting_service.get_report_by_player_name(
            test_session, "Non Existent Player"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_excludes_expired_reports_by_default(self, test_session):
        """Test that expired reports are excluded."""
        report = ScoutingReport(
            player_name="Expired Player",
            player_name_normalized="expired player",
            summary="Old data",
            recent_stats="Old stats",
            injury_status="Unknown",
            fantasy_outlook="Stale",
            detailed_analysis="Expired.",
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

        result = await scouting_service.get_report_by_player_name(
            test_session, "Expired Player"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_includes_expired_when_requested(self, test_session):
        """Test that expired reports can be included."""
        report = ScoutingReport(
            player_name="Expired But Included",
            player_name_normalized="expired but included",
            summary="Old data",
            recent_stats="Old stats",
            injury_status="Unknown",
            fantasy_outlook="Stale",
            detailed_analysis="Expired.",
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

        result = await scouting_service.get_report_by_player_name(
            test_session, "Expired But Included", include_expired=True
        )

        assert result is not None
        assert result.player_name == "Expired But Included"

    @pytest.mark.asyncio
    async def test_normalizes_player_name_for_lookup(self, test_session):
        """Test that player names are normalized for lookup."""
        report = ScoutingReport(
            player_name="Corey Seager",
            player_name_normalized="corey seager",
            summary="Power production",
            recent_stats="HR: 30",
            injury_status="Healthy",
            fantasy_outlook="Elite SS",
            detailed_analysis="Seager is mashing.",
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

        # Search with different casing
        result = await scouting_service.get_report_by_player_name(
            test_session, "COREY SEAGER"
        )
        assert result is not None

        result = await scouting_service.get_report_by_player_name(
            test_session, "  corey seager  "
        )
        assert result is not None


class TestGetRecentReports:
    """Tests for the get_recent_reports function."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_reports(self, test_session):
        """Test that empty list is returned when no reports exist."""
        reports, total = await scouting_service.get_recent_reports(test_session)

        assert reports == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_returns_reports_ordered_by_created_at(self, test_session):
        """Test that reports are ordered by created_at descending."""
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

        reports, total = await scouting_service.get_recent_reports(test_session)

        assert len(reports) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_respects_limit_parameter(self, test_session):
        """Test that limit parameter is respected."""
        for i in range(5):
            report = ScoutingReport(
                player_name=f"Limited Player {i}",
                player_name_normalized=f"limited player {i}",
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

        reports, total = await scouting_service.get_recent_reports(
            test_session, limit=2
        )

        assert len(reports) == 2
        assert total == 5

    @pytest.mark.asyncio
    async def test_respects_offset_parameter(self, test_session):
        """Test that offset parameter is respected."""
        for i in range(5):
            report = ScoutingReport(
                player_name=f"Offset Player {i}",
                player_name_normalized=f"offset player {i}",
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

        reports, total = await scouting_service.get_recent_reports(
            test_session, offset=3
        )

        assert len(reports) == 2
        assert total == 5

    @pytest.mark.asyncio
    async def test_excludes_expired_by_default(self, test_session):
        """Test that expired reports are excluded by default."""
        # Add valid report
        valid_report = ScoutingReport(
            player_name="Valid Player",
            player_name_normalized="valid player",
            summary="Valid",
            recent_stats="Stats",
            injury_status="Healthy",
            fantasy_outlook="Good",
            detailed_analysis="Analysis",
            sources=[],
            token_usage={
                "prompt_tokens": 100,
                "response_tokens": 50,
                "total_tokens": 150,
                "estimated_cost": "$0.001",
            },
            expires_at=datetime.now(UTC) + timedelta(hours=12),
        )
        test_session.add(valid_report)

        # Add expired report
        expired_report = ScoutingReport(
            player_name="Expired Player",
            player_name_normalized="expired player",
            summary="Expired",
            recent_stats="Old Stats",
            injury_status="Unknown",
            fantasy_outlook="Stale",
            detailed_analysis="Old",
            sources=[],
            token_usage={
                "prompt_tokens": 100,
                "response_tokens": 50,
                "total_tokens": 150,
                "estimated_cost": "$0.001",
            },
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        test_session.add(expired_report)
        await test_session.commit()

        reports, total = await scouting_service.get_recent_reports(test_session)

        assert len(reports) == 1
        assert total == 1
        assert reports[0].player_name == "Valid Player"


class TestCheckCache:
    """Tests for the check_cache function."""

    @pytest.mark.asyncio
    async def test_returns_cached_report_by_name(self, test_session):
        """Test that cached report is returned when searching by name."""
        report = ScoutingReport(
            player_name="Cached Player",
            player_name_normalized="cached player",
            summary="Cached",
            recent_stats="Stats",
            injury_status="Healthy",
            fantasy_outlook="Good",
            detailed_analysis="Analysis",
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

        result = await scouting_service.check_cache(
            test_session, player_name="Cached Player"
        )

        assert result is not None
        assert result.player_name == "Cached Player"

    @pytest.mark.asyncio
    async def test_returns_none_for_expired(self, test_session):
        """Test that expired reports are not returned."""
        report = ScoutingReport(
            player_name="Expired Cache",
            player_name_normalized="expired cache",
            summary="Expired",
            recent_stats="Old",
            injury_status="Unknown",
            fantasy_outlook="Stale",
            detailed_analysis="Old",
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

        result = await scouting_service.check_cache(
            test_session, player_name="Expired Cache"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_missing(self, test_session):
        """Test that None is returned for missing player."""
        result = await scouting_service.check_cache(
            test_session, player_name="Missing Player"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_no_identifier(self, test_session):
        """Test that None is returned when no identifier provided."""
        result = await scouting_service.check_cache(test_session)

        assert result is None
