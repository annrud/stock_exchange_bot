from asyncio import sleep
from collections import defaultdict
from logging import getLogger
from typing import TYPE_CHECKING

from app.game.models import GameModel
from app.telegram_bot.dataclasses import (
    CallbackQuery,
    Message,
    Update,
)

if TYPE_CHECKING:
    from app.web.app import Application


__all_ = ("CallbackManager",)


class CallbackManager:
    """Класс обработки обновлений типа 'callback_query'."""

    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("Callback_query handler")
        self.skip: dict[int, set[int]] = defaultdict(set)
        self.skip_all: bool = False

    async def handle_update_callback(self, update: Update) -> None:
        """Обработка обновлений типа 'callback_query'."""
        obj_callback = update.object.callback_query
        game = await self.app.store.game.find_active_game(
            chat_id=obj_callback.chat_id
        )
        if game is None:
            return
        player_name = self.app.game.service.get_user_name(
            username=obj_callback.from_.username,
            first_name=obj_callback.from_.first_name,
        )
        if obj_callback.data == "Join_the_game":
            await self.app.game.service.join_user_to_game(
                game=game, data=obj_callback.from_
            )
            await self.app.bot.api.answer_callback_query(
                callback_query=CallbackQuery(
                    callback_id=obj_callback.callback_id,
                    from_=obj_callback.from_,
                ),
                player_name=player_name,
                text=await self.app.store.game.get_phrase("joined_the_game"),
            )
            return
        user_telegram_id = obj_callback.from_.telegram_id
        if not self.app.game.service.is_participant(
            user_telegram_id=user_telegram_id, game=game
        ):
            return
        if obj_callback.data == self.app.bot.CONTINUE:
            if not await self.app.store.game.find_game_session(game_id=game.id):
                await self.handle_callback_continue(obj_callback=obj_callback)
            return
        if obj_callback.data.startswith((self.app.bot.BUY, self.app.bot.SELL)):
            await self.handle_callback_exchange(
                obj_callback=obj_callback, player_name=player_name
            )

        elif obj_callback.data.startswith(self.app.bot.SKIP):
            await self.handle_callback_skip(
                obj_callback=obj_callback, player_name=player_name, game=game
            )

    async def handle_callback_exchange(
        self, obj_callback: CallbackQuery, player_name: str
    ) -> None:
        """Обработка нажатия кнопки действия 'купить/продать акцию'.
        Отправка вопроса бота о количестве акций с интерфейсом ответа.
        """
        act, stock_title = obj_callback.data.split("_")
        force_reply_markup = self.app.game.reply_markup.get_force_reply_markup(
            placeholder_text="Введите количество здесь..."
        )
        await self.app.bot.api.send_message(
            message=Message(
                text=f"{player_name}, сколько акций {stock_title} "
                f"{self.app.bot.get_description(act)}?",
                chat_id=obj_callback.chat_id,
                reply_markup=force_reply_markup,
            )
        )

    async def handle_callback_skip(
        self, obj_callback: CallbackQuery, player_name: str, game: GameModel
    ) -> None:
        """Обработка нажатия действия 'Пропустить ход'."""
        await self.app.bot.api.answer_callback_query(
            callback_query=CallbackQuery(
                callback_id=obj_callback.callback_id,
                from_=obj_callback.from_,
            ),
            player_name=player_name,
            text=await self.app.store.game.get_phrase("skip_action"),
        )
        user = await self.app.store.user.get_user_by_telegram_id(
            telegram_id=obj_callback.from_.telegram_id
        )
        session = await self.app.store.game.find_game_session(game_id=game.id)
        self.skip[session.id].add(user.id)

        count_of_players = len(game.users)
        if len(self.skip.get(session.id, [])) == count_of_players:
            self.skip_all = True

    async def handle_callback_continue(
        self, obj_callback: CallbackQuery
    ) -> None:
        """Обработка нажатия действия 'Продолжить'."""
        game = await self.app.store.game.find_active_game(
            chat_id=obj_callback.chat_id
        )
        for _ in range(6):
            self.skip_all = False
            game_session = await self.app.bot.msg_manager.start_session(
                obj_callback=obj_callback
            )
            for _ in range(60):
                if self.skip_all:
                    break
                await sleep(1)
            game_session.is_finished = True
            await self.app.store.game.save_game_session(
                game_session=game_session
            )
            await self.app.bot.msg_manager.get_game_result(
                chat_id=obj_callback.chat_id
            )

        game.is_active = False
        await self.app.store.game.save_game(game)
        await self.app.bot.api.send_message(
            message=Message(
                text="Игра окончена.",
                chat_id=obj_callback.chat_id,
            )
        )
