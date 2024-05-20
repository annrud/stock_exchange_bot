"""Exchange table created

Revision ID: 014664121a5b
Revises: f21a39133f10
Create Date: 2024-05-18 22:35:29.937600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '014664121a5b'
down_revision: Union[str, None] = 'f21a39133f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exchange',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.String(), nullable=False),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('stock_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('execution_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['session.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['stock_id'], ['stock.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('exchange')
    # ### end Alembic commands ###
