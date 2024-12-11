"""Описание миграции

Revision ID: 67212ada65a1
Revises: 
Create Date: 2024-12-11 15:38:09.928928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67212ada65a1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('username', sa.String(), nullable=False),
                    sa.Column('hashed_password', sa.String(), nullable=False),
                    sa.Column('registered_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('is_superuser', sa.Boolean(), nullable=False),
                    sa.Column('is_verified', sa.Boolean(), nullable=False),
                    sa.Column('subscription_end', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('sessions',
                    sa.Column('session_id', sa.Integer(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('time1', sa.String(), nullable=True),
                    sa.Column('site1', sa.String(), nullable=True),
                    sa.Column('time2', sa.String(), nullable=True),
                    sa.Column('site2', sa.String(), nullable=True),
                    sa.Column('time3', sa.String(), nullable=True),
                    sa.Column('site3', sa.String(), nullable=True),
                    sa.Column('time4', sa.String(), nullable=True),
                    sa.Column('site4', sa.String(), nullable=True),
                    sa.Column('time5', sa.String(), nullable=True),
                    sa.Column('site5', sa.String(), nullable=True),
                    sa.Column('time6', sa.String(), nullable=True),
                    sa.Column('site6', sa.String(), nullable=True),
                    sa.Column('time7', sa.String(), nullable=True),
                    sa.Column('site7', sa.String(), nullable=True),
                    sa.Column('time8', sa.String(), nullable=True),
                    sa.Column('site8', sa.String(), nullable=True),
                    sa.Column('time9', sa.String(), nullable=True),
                    sa.Column('site9', sa.String(), nullable=True),
                    sa.Column('time10', sa.String(), nullable=True),
                    sa.Column('site10', sa.String(), nullable=True),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.Column('target', sa.Integer(), nullable=True),
                    sa.Column('confirmation', sa.Boolean(), nullable=True),
                    sa.Column('date', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('session_id')
                    )
    op.create_table('start_sessions',
                    sa.Column('session_id', sa.Integer(), nullable=True),
                    sa.Column('site1', sa.String(), nullable=True),
                    sa.Column('time1', sa.String(), nullable=True),
                    sa.Column('site2', sa.String(), nullable=True),
                    sa.Column('time2', sa.String(), nullable=True),
                    sa.Column('site3', sa.String(), nullable=True),
                    sa.Column('time3', sa.String(), nullable=True),
                    sa.Column('site4', sa.String(), nullable=True),
                    sa.Column('time4', sa.String(), nullable=True),
                    sa.Column('site5', sa.String(), nullable=True),
                    sa.Column('time5', sa.String(), nullable=True),
                    sa.Column('site6', sa.String(), nullable=True),
                    sa.Column('time6', sa.String(), nullable=True),
                    sa.Column('site7', sa.String(), nullable=True),
                    sa.Column('time7', sa.String(), nullable=True),
                    sa.Column('site8', sa.String(), nullable=True),
                    sa.Column('time8', sa.String(), nullable=True),
                    sa.Column('site9', sa.String(), nullable=True),
                    sa.Column('time9', sa.String(), nullable=True),
                    sa.Column('site10', sa.String(), nullable=True),
                    sa.Column('time10', sa.String(), nullable=True),
                    sa.Column('target', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('session_id')
                    )


def downgrade() -> None:
    pass
