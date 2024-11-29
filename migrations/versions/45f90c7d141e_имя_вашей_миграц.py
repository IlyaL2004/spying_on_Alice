"""Имя вашей миграц

Revision ID: 45f90c7d141e
Revises: fa0d65af50a2
Create Date: 2024-11-30 01:10:35.107029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '45f90c7d141e'
down_revision: Union[str, None] = 'fa0d65af50a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sessions', 'time1',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site1',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time2',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site2',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time3',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site3',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time4',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site4',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time5',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site5',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time6',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site6',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time7',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site7',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time8',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site8',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time9',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site9',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'time10',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'site10',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'email',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('sessions', 'target',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('sessions', 'confirmation',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('sessions', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('sessions', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('sessions', 'confirmation',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('sessions', 'target',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('sessions', 'email',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site10',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time10',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site9',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time9',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site8',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time8',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site7',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time7',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site6',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time6',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site5',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time5',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site4',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time4',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site3',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time3',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site2',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time2',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'site1',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('sessions', 'time1',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
