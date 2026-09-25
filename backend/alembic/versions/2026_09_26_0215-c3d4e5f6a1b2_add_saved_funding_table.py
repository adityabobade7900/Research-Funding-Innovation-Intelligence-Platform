"""Add saved_funding table for persistent funding watchlist

Revision ID: c3d4e5f6a1b2
Revises: 244ef6c34a82
Create Date: 2026-09-26 02:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a1b2'
down_revision: Union[str, None] = '244ef6c34a82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'saved_funding',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('funding_opportunity_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['funding_opportunity_id'], ['funding_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'funding_opportunity_id', name='uq_user_saved_funding')
    )
    op.create_index(op.f('ix_saved_funding_funding_opportunity_id'), 'saved_funding', ['funding_opportunity_id'], unique=False)
    op.create_index(op.f('ix_saved_funding_id'), 'saved_funding', ['id'], unique=False)
    op.create_index(op.f('ix_saved_funding_user_id'), 'saved_funding', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_saved_funding_user_id'), table_name='saved_funding')
    op.drop_index(op.f('ix_saved_funding_id'), table_name='saved_funding')
    op.drop_index(op.f('ix_saved_funding_funding_opportunity_id'), table_name='saved_funding')
    op.drop_table('saved_funding')
