"""Create user_history and partnership tables

Revision ID: create_user_history_partnership
Revises: d843b5f4a9c6
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'create_user_history_partnership'
down_revision = 'd843b5f4a9c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_history table
    op.create_table(
        'user_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('offer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.Enum('OFFER_VIEWED', 'OFFER_RESERVED', 'OFFER_CANCELLED', 'OFFER_COMPLETED', 'OFFER_EXPIRED', name='user_action'), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_history_user_id', 'user_history', ['user_id'], unique=False)
    op.create_index('idx_user_history_offer_id', 'user_history', ['offer_id'], unique=False)
    op.create_index('idx_user_history_action', 'user_history', ['action'], unique=False)
    op.create_index('idx_user_history_created_at', 'user_history', ['created_at'], unique=False)
    op.create_index('idx_user_history_user_created', 'user_history', ['user_id', 'created_at'], unique=False)

    # Create partnerships table
    op.create_table(
        'partnerships',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('place_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_partnerships_partner_user', 'partnerships', ['partner_user_id'], unique=False)
    op.create_index('idx_partnerships_place', 'partnerships', ['place_id'], unique=False)
    op.create_index('idx_partnerships_partner_place', 'partnerships', ['partner_user_id', 'place_id'], unique=False)
    op.create_index('idx_partnerships_active', 'partnerships', ['is_active'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_partnerships_active', table_name='partnerships')
    op.drop_index('idx_partnerships_partner_place', table_name='partnerships')
    op.drop_index('idx_partnerships_place', table_name='partnerships')
    op.drop_index('idx_partnerships_partner_user', table_name='partnerships')
    op.drop_table('partnerships')

    op.drop_index('idx_user_history_user_created', table_name='user_history')
    op.drop_index('idx_user_history_created_at', table_name='user_history')
    op.drop_index('idx_user_history_action', table_name='user_history')
    op.drop_index('idx_user_history_offer_id', table_name='user_history')
    op.drop_index('idx_user_history_user_id', table_name='user_history')
    op.drop_table('user_history')
