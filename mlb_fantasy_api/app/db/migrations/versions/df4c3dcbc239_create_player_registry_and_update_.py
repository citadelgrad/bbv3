"""create player registry and update scouting reports

Revision ID: df4c3dcbc239
Revises: 28913cc30846
Create Date: 2025-12-30 15:24:21.681517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'df4c3dcbc239'
down_revision: Union[str, Sequence[str], None] = '28913cc30846'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create player_name_aliases table
    op.create_table('player_name_aliases',
    sa.Column('player_id', sa.UUID(), nullable=False),
    sa.Column('alias_name', sa.String(length=150), nullable=False),
    sa.Column('alias_normalized', sa.String(length=150), nullable=False),
    sa.Column('alias_type', sa.String(length=20), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('player_id', 'alias_normalized', name='uq_player_alias')
    )
    op.create_index(op.f('ix_player_name_aliases_alias_normalized'), 'player_name_aliases', ['alias_normalized'], unique=False)
    op.create_index(op.f('ix_player_name_aliases_player_id'), 'player_name_aliases', ['player_id'], unique=False)

    # Add new columns to players table
    op.add_column('players', sa.Column('full_name', sa.String(length=150), nullable=False))
    op.add_column('players', sa.Column('name_normalized', sa.String(length=150), nullable=False))
    op.add_column('players', sa.Column('first_name', sa.String(length=50), nullable=False))
    op.add_column('players', sa.Column('last_name', sa.String(length=50), nullable=False))
    op.add_column('players', sa.Column('name_suffix', sa.String(length=10), nullable=True))
    op.add_column('players', sa.Column('baseball_reference_id', sa.String(length=20), nullable=True))
    op.add_column('players', sa.Column('yahoo_fantasy_id', sa.String(length=30), nullable=True))
    op.add_column('players', sa.Column('espn_fantasy_id', sa.String(length=30), nullable=True))
    op.add_column('players', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('players', sa.Column('current_team', sa.String(length=50), nullable=True))
    op.add_column('players', sa.Column('current_team_abbrev', sa.String(length=5), nullable=True))
    op.add_column('players', sa.Column('primary_position', sa.String(length=10), nullable=True))
    op.add_column('players', sa.Column('bats', sa.String(length=1), nullable=True))
    op.add_column('players', sa.Column('throws', sa.String(length=1), nullable=True))
    op.add_column('players', sa.Column('status', sa.String(length=20), server_default='active', nullable=False))
    # Note: is_active column already exists from original schema
    op.add_column('players', sa.Column('mlb_org', sa.String(length=50), nullable=True))
    op.add_column('players', sa.Column('minor_league_level', sa.String(length=10), nullable=True))
    op.add_column('players', sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('players', sa.Column('data_source', sa.String(length=50), nullable=True))
    op.alter_column('players', 'fangraphs_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=20),
               existing_nullable=True)
    op.drop_index(op.f('ix_players_name'), table_name='players')
    op.create_index(op.f('ix_players_baseball_reference_id'), 'players', ['baseball_reference_id'], unique=True)
    op.create_index(op.f('ix_players_current_team_abbrev'), 'players', ['current_team_abbrev'], unique=False)
    op.create_index(op.f('ix_players_espn_fantasy_id'), 'players', ['espn_fantasy_id'], unique=True)
    op.create_index(op.f('ix_players_fangraphs_id'), 'players', ['fangraphs_id'], unique=True)
    op.create_index(op.f('ix_players_full_name'), 'players', ['full_name'], unique=False)
    op.create_index(op.f('ix_players_name_normalized'), 'players', ['name_normalized'], unique=False)
    op.create_index(op.f('ix_players_status'), 'players', ['status'], unique=False)
    op.create_index(op.f('ix_players_yahoo_fantasy_id'), 'players', ['yahoo_fantasy_id'], unique=True)
    op.drop_column('players', 'position')
    op.drop_column('players', 'team')
    op.drop_column('players', 'metadata')
    op.drop_column('players', 'name')
    # Add versioning columns to scouting_reports
    op.add_column('scouting_reports', sa.Column('player_id', sa.UUID(), nullable=True))
    op.add_column('scouting_reports', sa.Column('version', sa.Integer(), server_default='1', nullable=False))
    op.add_column('scouting_reports', sa.Column('is_current', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    op.add_column('scouting_reports', sa.Column('previous_version_id', sa.UUID(), nullable=True))
    op.add_column('scouting_reports', sa.Column('trigger_reason', sa.String(length=50), nullable=True))
    op.add_column('scouting_reports', sa.Column('source_url', sa.String(length=500), nullable=True))
    op.alter_column('scouting_reports', 'player_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.alter_column('scouting_reports', 'player_name_normalized',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.drop_index(op.f('ix_scouting_reports_player_name_normalized'), table_name='scouting_reports')
    op.create_index(op.f('ix_scouting_reports_player_name_normalized'), 'scouting_reports', ['player_name_normalized'], unique=False)
    op.create_index(op.f('ix_scouting_reports_is_current'), 'scouting_reports', ['is_current'], unique=False)
    op.create_index(op.f('ix_scouting_reports_player_id'), 'scouting_reports', ['player_id'], unique=False)
    op.create_foreign_key(None, 'scouting_reports', 'scouting_reports', ['previous_version_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'scouting_reports', 'players', ['player_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Remove scouting_reports foreign keys and new columns
    op.drop_constraint('scouting_reports_player_id_fkey', 'scouting_reports', type_='foreignkey')
    op.drop_constraint('scouting_reports_previous_version_id_fkey', 'scouting_reports', type_='foreignkey')
    op.drop_index(op.f('ix_scouting_reports_player_id'), table_name='scouting_reports')
    op.drop_index(op.f('ix_scouting_reports_is_current'), table_name='scouting_reports')
    op.drop_index(op.f('ix_scouting_reports_player_name_normalized'), table_name='scouting_reports')
    op.create_index(op.f('ix_scouting_reports_player_name_normalized'), 'scouting_reports', ['player_name_normalized'], unique=True)
    op.alter_column('scouting_reports', 'player_name_normalized',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.alter_column('scouting_reports', 'player_name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.drop_column('scouting_reports', 'source_url')
    op.drop_column('scouting_reports', 'trigger_reason')
    op.drop_column('scouting_reports', 'previous_version_id')
    op.drop_column('scouting_reports', 'is_current')
    op.drop_column('scouting_reports', 'version')
    op.drop_column('scouting_reports', 'player_id')

    # Restore old players columns
    op.add_column('players', sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('players', sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('players', sa.Column('team', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('players', sa.Column('position', sa.VARCHAR(length=50), autoincrement=False, nullable=True))

    # Remove new players indexes and columns
    op.drop_index(op.f('ix_players_yahoo_fantasy_id'), table_name='players')
    op.drop_index(op.f('ix_players_status'), table_name='players')
    op.drop_index(op.f('ix_players_name_normalized'), table_name='players')
    op.drop_index(op.f('ix_players_full_name'), table_name='players')
    op.drop_index(op.f('ix_players_fangraphs_id'), table_name='players')
    op.drop_index(op.f('ix_players_espn_fantasy_id'), table_name='players')
    op.drop_index(op.f('ix_players_current_team_abbrev'), table_name='players')
    op.drop_index(op.f('ix_players_baseball_reference_id'), table_name='players')
    op.create_index(op.f('ix_players_name'), 'players', ['name'], unique=False)
    op.alter_column('players', 'fangraphs_id',
               existing_type=sa.String(length=20),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # Note: is_active column existed before this migration, don't drop it
    op.drop_column('players', 'data_source')
    op.drop_column('players', 'last_synced_at')
    op.drop_column('players', 'minor_league_level')
    op.drop_column('players', 'mlb_org')
    op.drop_column('players', 'status')
    op.drop_column('players', 'throws')
    op.drop_column('players', 'bats')
    op.drop_column('players', 'primary_position')
    op.drop_column('players', 'current_team_abbrev')
    op.drop_column('players', 'current_team')
    op.drop_column('players', 'birth_date')
    op.drop_column('players', 'espn_fantasy_id')
    op.drop_column('players', 'yahoo_fantasy_id')
    op.drop_column('players', 'baseball_reference_id')
    op.drop_column('players', 'name_suffix')
    op.drop_column('players', 'last_name')
    op.drop_column('players', 'first_name')
    op.drop_column('players', 'name_normalized')
    op.drop_column('players', 'full_name')

    # Drop player_name_aliases table
    op.drop_index(op.f('ix_player_name_aliases_player_id'), table_name='player_name_aliases')
    op.drop_index(op.f('ix_player_name_aliases_alias_normalized'), table_name='player_name_aliases')
    op.drop_table('player_name_aliases')
