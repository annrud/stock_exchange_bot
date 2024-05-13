import asyncio
import typing
from logging import getLogger

from app.telegram_bot.dataclasses import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    UpdateMessage,
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


__all_ = ("BotManager",)


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")

    async def start(self, obj_message: UpdateMessage) -> None:
        if await self.app.store.game.get_active_game(
            chat_id=obj_message.chat_id
        ):
            self.logger.info(
                "Calling the /start command while the game is running"
            )
            return
        await self.app.store.game.connect(
            app=self.app, chat_id=obj_message.chat_id, data=obj_message.from_
        )
        text = await self.app.store.game.get_phrase("text_to_start")
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
        await self.app.bot.api.send_message(
            Message(
                chat_id=obj_message.chat_id,
                text=text,
                reply_markup=reply_markup,
            )
        )
        try:
            async with asyncio.timeout(30):
                while True:
                    await self.app.bot.api.poll()
        except TimeoutError:
            self.logger.info("timeout!")
        players_id = await self.app.store.game.get_users_id_from_game(
            obj_message.chat_id
        )
        if len(players_id) < 2:
            await self.app.store.game.deactivate_the_game(obj_message.chat_id)
            await self.app.bot.api.send_message(
                Message(
                    text=await self.app.store.game.get_phrase(
                        "absence_of_participants"
                    ),
                    chat_id=obj_message.chat_id,
                    reply_markup={},
                )
            )
            self.logger.info("Game stopped: participants have not joined")
        else:
            await self.app.bot.api.send_message(
                Message(
                    text=await self.app.store.game.get_phrase("game_started"),
                    chat_id=obj_message.chat_id,
                    reply_markup={},
                )
            )

    async def stop(self, obj_message: UpdateMessage) -> None:
        players_id = await self.app.store.game.get_users_id_from_game(
            obj_message.chat_id
        )
        user = await self.app.store.user.get_user_by_telegram_id(
            obj_message.from_.telegram_id
        )
        if user is not None and user.id in players_id:
            await self.app.store.game.deactivate_the_game(obj_message.chat_id)
            await self.app.bot.api.send_message(
                Message(
                    text=await self.app.store.game.get_phrase("game_stopped"),
                    chat_id=obj_message.chat_id,
                    reply_markup={},
                )
            )
            self.logger.info("Game stopped")

    async def handler_update_message(self, update: Update):
        obj_message = update.object.message
        if (
            obj_message.entities
            and obj_message.entities[0].type == "bot_command"
        ):
            bot = await self.app.bot.api.get_me()
            bot_username = bot.username if bot else ""
            if obj_message.text in ("/start", f"/start@{bot_username}"):
                await self.start(obj_message)
            if obj_message.text in ("/stop", f"/stop@{bot_username}"):
                await self.stop(obj_message)

    async def handler_update_callback(self, update: Update):
        obj_callback = update.object.callback_query
        if obj_callback.data == "Join_the_game":
            await self.app.store.game.add_user_to_game(
                chat_id=obj_callback.chat_id, data=obj_callback.from_
            )
            await self.app.bot.api.answer_callback_query(
                CallbackQuery(
                    callback_id=obj_callback.callback_id,
                    from_=obj_callback.from_,
                ),
            )
