"""Content added to Phrase

Revision ID: de6d50242f2d
Revises: b5e3a398d283
Create Date: 2024-05-13 22:29:11.957996

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

data = [
    {"key": "text_to_start", "phrase": "Игра 'Биржа': каждому игроку выдается по 100y.e, вначале игры, игроки делают ходы по очереди. Для присоединения к игре у вас есть 30 секунд."},
    {"key": "absence_of_participants", "phrase": "Игра <b>Биржа</b> остановлена: никто не присоединился. 😩"},
    {"key": "game_started", "phrase": "Игра <b>Биржа</b> запущена. 🚀"},
    {"key": "game_stopped", "phrase": "Игра <b>Биржа</b> остановлена. ❌"},
]

# revision identifiers, used by Alembic.
revision: str = 'de6d50242f2d'
down_revision: Union[str, None] = 'b5e3a398d283'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    metadata = sa.MetaData()
    phrase = sa.Table(
        "phrase",
        metadata,
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("phrase", sa.String),
    )

    conn.execute(
        phrase.insert(),
        data
    )


def downgrade() -> None:
    op.execute("DELETE FROM phrase WHERE key IN ('text_to_start', 'absence_of_participants', 'game_started', 'game_stopped')")

