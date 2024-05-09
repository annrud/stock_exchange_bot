import asyncio
import typing
from logging import getLogger

from app.store.telegram_api.dataclasses import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application

dict_phrases = {
    "rules_of_the_game": "Игра Биржа: каждому игроку выдается по 100y.e. "
    "вначале игры, игроки делают ходы по очереди",
    "text_to_start": "Для присоединения к игре у вас есть 30 секунд",
}


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handler_update_message(self, update: Update):
        text = update.object.message.text
        reply_markup = {}
        if (
            update.object.message.entities
            and update.object.message.entities[0].type == "bot_command"
            and update.object.message.text == "/start"
        ):
            text = dict_phrases["text_to_start"]
            inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[])
            inline_button = [
                InlineKeyboardButton(
                    text="Присоединиться к игре",
                    callback_data="Join_the_game",
                )
            ]
            inline_keyboard_markup.inline_keyboard.append(inline_button)
            reply_markup = {
                "inline_keyboard": [
                    [button.to_dict() for button in row]
                    for row in inline_keyboard_markup.inline_keyboard
                ]
            }
        if text:
            await self.app.store.telegram_api.send_message(
                Message(
                    chat_id=update.object.message.chat_id,
                    text=text,
                    reply_markup=reply_markup,
                )
            )

    async def handler_update_callback(self, update: Update):
        if update.object.callback_query.data == "Join_the_game":
            await self.app.store.telegram_api.answer_callback_query(
                CallbackQuery(
                    callback_id=update.object.callback_query.callback_id,
                    from_=update.object.callback_query.from_,
                ),
            )
            await asyncio.sleep(30)
            await self.app.store.telegram_api.send_message(
                Message(
                    text="Активы",
                    chat_id=update.object.callback_query.chat_id,
                    reply_markup={},
                )
            )
