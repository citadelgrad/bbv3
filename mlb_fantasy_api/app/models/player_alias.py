"""Player name alias model for alternate names and nicknames."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.player import Player


class PlayerNameAlias(Base, UUIDMixin, TimestampMixin):
    """Alternative names and nicknames for players.

    Supports lookups by nicknames (e.g., "Shohei" for "Shohei Ohtani"),
    legal name changes, and common abbreviations.
    """

    __tablename__ = "player_name_aliases"

    player_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alias_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    alias_normalized: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )
    alias_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="nickname",
    )  # nickname, legal_change, abbreviation, maiden_name

    # Relationship
    player: Mapped["Player"] = relationship(
        back_populates="name_aliases",
    )

    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "alias_normalized",
            name="uq_player_alias",
        ),
    )

    def __repr__(self) -> str:
        return f"<PlayerNameAlias {self.alias_name} -> player_id={self.player_id}>"
