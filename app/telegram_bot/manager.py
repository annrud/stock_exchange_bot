import asyncio
import typing
from logging import getLogger

from app.telegram_bot.dataclasses import (
    CallbackQuery,
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

    async def info(
        self, obj_message: UpdateMessage, session_id: int | None = None
    ) -> None:
        chat_id = obj_message.chat_id
        stock_price = await self.app.game.service.get_stock_price(
            chat_id=chat_id, session_id=session_id
        )
        if stock_price is None:
            text = await self.app.store.game.get_phrase("game_is_not_running")
        else:
            text = "Котировки (цена в у.е.):\n" + stock_price
        await self.app.bot.api.send_message(
            Message(
                text=text,
                chat_id=chat_id,
                reply_markup={},
            )
        )

    async def start_session(
        self, obj_message: UpdateMessage, players_telegram_id: list[int]
    ) -> None:
        chat_id = obj_message.chat_id
        game = await self.app.store.game.find_active_game(chat_id=chat_id)
        if game is None:
            return
        game_session = await self.app.game.service.create_session(
            game_id=game.id
        )
        stocks = await self.app.store.game.get_stocks()
        for stock in stocks:
            await self.app.game.service.create_session_stock(
                session_id=game_session.id, stock_id=stock.id
            )
        await self.info(obj_message=obj_message, session_id=game_session.id)

        await self.app.bot.api.send_message(
            Message(
                text="Выберите 👇",
                chat_id=chat_id,
                reply_markup=self.app.game.reply_markup_service.create_start_session_reply_markup(
                    players_telegram_id
                ),
            )
        )

    async def start(self, obj_message: UpdateMessage) -> None:
        chat_id = obj_message.chat_id
        game = await self.app.store.game.find_active_game(chat_id)
        if game:
            self.logger.info(
                "Calling the /start command while the game is running"
            )
            return
        game = await self.app.game.service.create_game(
            chat_id=chat_id, data=obj_message.from_
        )
        await self.app.game.service.join_user_to_game(
            game, data=obj_message.from_
        )
        await self.app.bot.api.send_message(
            Message(
                chat_id=chat_id,
                text=await self.app.store.game.get_phrase("text_to_start"),
                reply_markup=self.app.game.reply_markup_service.create_start_reply_markup(),
            )
        )
        try:
            async with asyncio.timeout(30):
                while True:
                    await self.app.bot.api.poll()
        except TimeoutError:
            self.logger.info("timeout join the game!")
        game = await self.app.store.game.find_active_game(chat_id)
        if len(game.users) < 2:
            await self.app.game.service.deactivate_game(game)
            await self.app.bot.api.send_message(
                Message(
                    text=await self.app.store.game.get_phrase(
                        "absence_of_participants"
                    ),
                    chat_id=chat_id,
                    reply_markup={},
                )
            )
            self.logger.info("Game stopped: participants have not joined")
            return

        players_telegram_id: list[int] = []
        players_name: str = ""
        for game_user in game.users:
            players_telegram_id.append(game_user.user.telegram_id)
            players_name += (
                f"@{game_user.user.username}\n"
                if game_user.user.username
                else f"{game_user.user.first_name}\n"
            )

        await self.app.bot.api.send_message(
            Message(
                text=await self.app.store.game.get_phrase("game_started")
                + f"\nИгроки: \n{players_name}",
                chat_id=chat_id,
                reply_markup={},
            )
        )

        await self.start_session(
            obj_message=obj_message, players_telegram_id=players_telegram_id
        )

    async def stop(self, obj_message: UpdateMessage) -> None:
        game = await self.app.store.game.find_active_game(obj_message.chat_id)
        user = await self.app.store.user.get_user_by_telegram_id(
            obj_message.from_.telegram_id
        )
        players_telegram_ids = (
            game_user.user.telegram_id for game_user in game.users
        )
        if user is not None and user.telegram_id in players_telegram_ids:
            await self.app.game.service.deactivate_game(game=game)
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
            if obj_message.text in ("/info", f"/info@{bot_username}"):
                await self.info(obj_message)

    async def handler_update_callback(self, update: Update):
        obj_callback = update.object.callback_query
        if obj_callback.data == "Join_the_game":
            game = await self.app.store.game.find_active_game(
                obj_callback.chat_id
            )
            if game is None:
                return
            await self.app.game.service.join_user_to_game(
                game, data=obj_callback.from_
            )

            await self.app.bot.api.answer_callback_query(
                CallbackQuery(
                    callback_id=obj_callback.callback_id,
                    from_=obj_callback.from_,
                ),
            )
        if obj_callback.data.startswith("Buy_"):
            _, players_telegram_id = obj_callback.data.split("_")
            players_id = eval(players_telegram_id)
            user_telegram_id = obj_callback.from_.telegram_id
            if user_telegram_id not in players_id:
                return
