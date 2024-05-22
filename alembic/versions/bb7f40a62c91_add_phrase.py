"""Add phrase

Revision ID: bb7f40a62c91
Revises: c72286b3f32b
Create Date: 2024-05-17 10:22:43.279605

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

data = [
    {"key": "no_data_available", "phrase": "Данные отсутствуют. 🤖"},
    {"key": "game_is_already_running", "phrase": "Игра <b>Биржа</b> уже запущена. 🤖"},
    {"key": "game_is_already_stopped", "phrase": "Игра <b>Биржа</b> уже остановлена. 🤖"},
    {"key": "reply_awaited", "phrase": "❗ При отправке ответа, пожалуйста, убедитесь, что ваше сообщение отправляется именно <b>реплаем</b> в ответ на вопрос бота. Если по какой-то причине это не так, зажмите сообщение с пришедшим вопросом и нажмите Reply/Ответить."},
    {"key": "start_message", "phrase": ("Игра <b>Биржа</b> состоит из <b>6 раундов</b>. 🎯\n\n"
                                        "На каждом раунде <b><i>котировки меняются</i></b>. 📊\n\n"
                                        "Количество игроков не ограничено. ✅\n\n"
                                        "Вначале игры каждому игроку выдается по <b>100y.e.</b> 💵\n\n"
                                        "❗ Для присоединения к игре у вас есть <b>30 секунд</b>. ⏱")},
    {"key": "session_info", "phrase": ("Каждый раунд длится <b>1 минуту</b> ⏳.\n\n"
                                       "Количество покупок и продаж акций не ограничено 🔁.\n\n"
                                       "Для совершения сделки нажмите кнопку <b>Купить</b> или <b>Продать</b> с соответствующей акцией, а затем отправьте ответ с количеством акций боту.")},
    {"key": "joined_the_game", "phrase": "присоединился(ась) к игре."},
    {"key": "skip_action", "phrase": "пропустил(а) ход. ⏩"},
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
