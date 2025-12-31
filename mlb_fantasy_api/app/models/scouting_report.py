import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.player import Player


class ScoutingReport(Base, UUIDMixin, TimestampMixin):
    """Immutable scouting report linked to a canonical player.

    Reports are versioned - each new report creates a new version
    while marking the previous as not current.
    """

    __tablename__ = "scouting_reports"

    # Player identification - linked to Player registry
    player_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=True,  # Nullable during migration, will be required later
        index=True,
    )

    # DEPRECATED: Keep for migration, will be removed later
    player_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,  # Changed to nullable for new records
    )
    player_name_normalized: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,  # Changed to nullable for new records
        index=True,
    )

    # Versioning (immutable reports)
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )
    previous_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scouting_reports.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Report trigger metadata
    trigger_reason: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # scheduled, user_request, performance_change, injury_update, trade
    source_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Relationship to Player
    player: Mapped["Player | None"] = relationship(
        back_populates="scouting_reports",
    )

    # Report content
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    recent_stats: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    injury_status: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    fantasy_outlook: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    detailed_analysis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Metadata
    sources: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    token_usage: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
