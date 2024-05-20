"""Deleted field 'title' and added field 'number' to Session

Revision ID: e6aae87d36df
Revises: de6d50242f2d
Create Date: 2024-05-14 14:50:53.447364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6aae87d36df'
down_revision: Union[str, None] = 'de6d50242f2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('session', sa.Column('number', sa.Integer(), nullable=False))
    op.drop_column('session', 'title')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('session', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('session', 'number')
    # ### end Alembic commands ###