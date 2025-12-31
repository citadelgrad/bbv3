"""Player model for the master player registry."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.player_alias import PlayerNameAlias
    from app.models.scouting_report import ScoutingReport


class Player(Base, UUIDMixin, TimestampMixin):
    """Master player registry for MLB/MiLB players.

    Stores canonical player identity with external ID mappings
    to enable cross-platform integration (Yahoo Fantasy, FanGraphs, etc.).
    """

    __tablename__ = "players"

    # Canonical name
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    name_normalized: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    # Name components for disambiguation
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    name_suffix: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )  # Jr., III, etc.

    # External identifiers
    mlb_id: Mapped[int | None] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
        index=True,
    )
    fangraphs_id: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )
    baseball_reference_id: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
        index=True,
    )

    # Fantasy platform IDs (for future integration)
    yahoo_fantasy_id: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
        index=True,
    )
    espn_fantasy_id: Mapped[str | None] = mapped_column(
        String(30),
        unique=True,
        nullable=True,
        index=True,
    )

    # Player metadata
    birth_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    current_team: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    current_team_abbrev: Mapped[str | None] = mapped_column(
        String(5),
        nullable=True,
        index=True,
    )
    primary_position: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )  # C, 1B, SP, RP, etc.
    bats: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True,
    )  # L, R, S
    throws: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True,
    )  # L, R

    # Player status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        index=True,
    )  # active, inactive, retired, minors

    # MiLB-specific
    mlb_org: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # Parent MLB organization
    minor_league_level: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )  # AAA, AA, A+, A, etc.

    # Data quality tracking
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    data_source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # "mlb_api", "fangraphs", "manual", etc.

    # Active flag for soft deletes
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships
    scouting_reports: Mapped[list["ScoutingReport"]] = relationship(
        back_populates="player",
        lazy="selectin",
    )
    name_aliases: Mapped[list["PlayerNameAlias"]] = relationship(
        back_populates="player",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Player {self.full_name} (mlb_id={self.mlb_id})>"
