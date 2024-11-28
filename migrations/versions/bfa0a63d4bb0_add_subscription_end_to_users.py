"""Add subscription_end to Users

Revision ID: bfa0a63d4bb0
Revises: b91bb3e55cd5
Create Date: 2024-11-27 21:23:34.930636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bfa0a63d4bb0'
down_revision: Union[str, None] = 'b91bb3e55cd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('access_tokens')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('access_tokens',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('expires_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='access_tokens_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='access_tokens_pkey')
    )
    # ### end Alembic commands ###
