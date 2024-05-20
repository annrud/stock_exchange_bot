"""Add phrase

Revision ID: bb7f40a62c91
Revises: c72286b3f32b
Create Date: 2024-05-17 10:22:43.279605

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

data = [
    {"key": "no_data_available", "phrase": "Данные отсутствуют."},
    {"key": "game_is_already_running", "phrase": "Игра 'Биржа' уже запущена."},
    {"key": "game_is_already_stopped", "phrase": "Игра 'Биржа' уже остановлена."},
    {"key": "reply_awaited", "phrase": "При отправке ответа, пожалуйста, убедитесь, что ваше сообщение отправляется именно реплаем в ответ на вопрос бота. Если по какой-то причине это не так, зажмите сообщение с пришедшим вопросом и нажмите Reply/Ответить."},
    {"key": "start_message", "phrase": "Игра 'Биржа' состоит из 6 раундов. На каждом раунде котировки меняются. Количество игроков не ограничено. Вначале игры каждому игроку выдается по 100y.e. Для присоединения к игре у вас есть 30 секунд."},
    {"key": "session_info", "phrase": "Каждый раунд длится 1 минуту. Количество покупок и продаж акций не ограничено. Для совершения сделки нажмите кнопку 'купить' или 'продать' с соответствующей акцией, а затем отправьте ответ с количеством акций боту."}
    {"key": "joined_the_game", "phrase": "присоединился(ась) к игре."},
    {"key": "skip_action", "phrase": "пропустил(а) ход."},
]

# revision identifiers, used by Alembic.
revision: str = 'bb7f40a62c91'
down_revision: Union[str, None] = 'c72286b3f32b'
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
    op.execute(
        "DELETE FROM phrase WHERE key IN ('no_data_available', 'game_is_already_running', 'game_is_already_stopped', 'reply_awaited', 'start_message', 'session_info', 'joined_the_game', 'skip_action')")
