"""Fill Stock table with initial data

Revision ID: c72286b3f32b
Revises: e6aae87d36df
Create Date: 2024-05-14 17:34:39.085060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

initial_stock_data = [
    {"title": "Apple"},
    {"title": "Microsoft"},
    {"title": "Amazon"},
    {"title": "Google"},
    {"title": "Facebook"},
    {"title": "Tesla"},
]

# revision identifiers, used by Alembic.
revision: str = 'c72286b3f32b'
down_revision: Union[str, None] = 'e6aae87d36df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    stock_table = table(
        'stock',
        column('id', sa.Integer),
        column('title', sa.String),
    )

    op.bulk_insert(stock_table, initial_stock_data)


def downgrade() -> None:
    op.execute("DELETE FROM stock WHERE title IN ('Apple', 'Microsoft', 'Amazon', 'Google', 'Facebook', 'Tesla')")
