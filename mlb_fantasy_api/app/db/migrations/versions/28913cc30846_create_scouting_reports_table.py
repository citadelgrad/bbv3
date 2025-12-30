"""create scouting_reports table

Revision ID: 28913cc30846
Revises: 40d1af4434b3
Create Date: 2025-12-30 11:32:16.567430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '28913cc30846'
down_revision: Union[str, Sequence[str], None] = '40d1af4434b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('scouting_reports',
    sa.Column('player_name', sa.String(length=100), nullable=False),
    sa.Column('player_name_normalized', sa.String(length=100), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('recent_stats', sa.Text(), nullable=False),
    sa.Column('injury_status', sa.String(length=200), nullable=False),
    sa.Column('fantasy_outlook', sa.Text(), nullable=False),
    sa.Column('detailed_analysis', sa.Text(), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('token_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scouting_reports_expires_at'), 'scouting_reports', ['expires_at'], unique=False)
    op.create_index(op.f('ix_scouting_reports_player_name_normalized'), 'scouting_reports', ['player_name_normalized'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_scouting_reports_player_name_normalized'), table_name='scouting_reports')
    op.drop_index(op.f('ix_scouting_reports_expires_at'), table_name='scouting_reports')
    op.drop_table('scouting_reports')
