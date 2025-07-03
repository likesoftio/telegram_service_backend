"""create users table

Revision ID: 0001
Revises: 
Create Date: 2024-06-07
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('telegram_id', sa.String, unique=True, index=True, nullable=False),
        sa.Column('username', sa.String, index=True),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('email', sa.String, unique=True, index=True, nullable=True),
        sa.Column('password_hash', sa.String, nullable=True),
    )

def downgrade():
    op.drop_table('users') 