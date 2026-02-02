"""Create users and verification_tokens tables

Revision ID: create_auth_tables
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'create_auth_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='unique_users_email')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_role', 'users', ['role'], unique=False)
    op.create_index('idx_users_is_verified', 'users', ['is_verified'], unique=False)

    # Create verification_tokens table
    op.create_table(
        'verification_tokens',
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('token'),
        sa.UniqueConstraint('token', name='unique_verification_tokens_token')
    )
    op.create_index('idx_verification_tokens_user_id', 'verification_tokens', ['user_id'], unique=False)
    op.create_index('idx_verification_tokens_expires_at', 'verification_tokens', ['expires_at'], unique=False)
    op.create_index('idx_verification_tokens_used', 'verification_tokens', ['used'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_verification_tokens_used', table_name='verification_tokens')
    op.drop_index('idx_verification_tokens_expires_at', table_name='verification_tokens')
    op.drop_index('idx_verification_tokens_user_id', table_name='verification_tokens')
    op.drop_table('verification_tokens')

    op.drop_index('idx_users_is_verified', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
