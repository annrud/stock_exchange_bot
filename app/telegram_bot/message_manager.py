from asyncio import sleep
from logging import getLogger
from typing import TYPE_CHECKING

from app.game.models import Exchange, GameUser, Session, Stock
from app.telegram_bot.dataclasses import (
    CallbackQuery,
    Message,
    Update,
    UpdateMessage,
)

if TYPE_CHECKING:
    from app.web.app import Application


__all_ = ("MessageManager",)


class MessageManager:
    """Класс обработки обновлений типа 'message'."""

    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("Message handler")

    async def handle_update_message(self, update: Update):
        """Обработка обновлений типа 'message'."""
        obj_message = update.object.message
        if (
            obj_message.entities
            and obj_message.entities[0].type == "bot_command"
        ):
            bot = await self.app.bot.api.get_me()
            bot_username = bot.username if bot else ""
            if obj_message.text in ("/start", f"/start@{bot_username}"):
                await self.start(obj_message=obj_message)
            elif obj_message.text in ("/stop", f"/stop@{bot_username}"):
                await self.stop(obj_message=obj_message)
            elif obj_message.text in ("/info", f"/info@{bot_username}"):
                await self.info(obj_message=obj_message)
        elif obj_message.reply_to_message:
            await self.start_exchange(obj_message=obj_message)

    async def info(self, obj_message: UpdateMessage) -> None:
        """Выдача информации об акциях игрока."""
        user_telegram_id = obj_message.from_.telegram_id
        user = await self.app.store.user.get_user_by_telegram_id(
            telegram_id=user_telegram_id
        )
        game = await self.app.store.game.find_active_game(obj_message.chat_id)
        if not user or not game:
            text = await self.app.store.game.get_phrase("no_data_available")
        else:
            user_name = self.app.game.service.get_user_name(
                username=user.username, first_name=user.first_name
            )
            str_user_stocks = (
                await self.app.game.service.get_str_user_stock_quantity(
                    game_id=game.id, user_id=user.id
                )
            )
            if not str_user_stocks:
                text = f"{user_name}, у вас нет приобретенных акций."
            else:
                game_user = await self.app.store.game.find_game_user(
                    game_id=game.id, user_id=user.id
                )
                text = (
                    f"{user_name}, ваш портфель 💼:\n{str_user_stocks}\n"
                    f"Наличные 💷: {game_user.cash_balance} y.e."
                )
        reply_to_message_id = obj_message.message_id
        await self.app.bot.api.send_message(
            message=Message(
                text=text,
                chat_id=obj_message.chat_id,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def get_quotes(
        self, chat_id: str, session_id: int | None = None
    ) -> None:
        """Выдача информации по текущим котировкам."""
        str_stocks_price = await self.app.game.service.get_str_stocks_price(
            chat_id=chat_id, session_id=session_id
        )
        text = "🎲 Котировки (цена в у.е.):\n" + str_stocks_price
        await self.app.bot.api.send_message(
            message=Message(
                text=text,
                chat_id=chat_id,
            )
        )

    async def start(self, obj_message: UpdateMessage) -> None:
        """Запуск игры."""
        chat_id = obj_message.chat_id
        game = await self.app.store.game.find_active_game(chat_id)
        if game:
            self.logger.info(
                "Calling the /start command while the game is running"
            )
            await self.app.bot.api.send_message(
                message=Message(
                    chat_id=chat_id,
                    text=await self.app.store.game.get_phrase(
                        "game_is_already_running"
                    ),
                )
            )
            return
        game = await self.app.game.service.create_game(
            chat_id=chat_id, data=obj_message.from_
        )
        await self.app.game.service.join_user_to_game(
            game, data=obj_message.from_
        )
        await self.app.bot.api.send_message(
            message=Message(
                chat_id=chat_id,
                text=await self.app.store.game.get_phrase("start_message"),
                reply_markup=self.app.game.reply_markup.create_start(),
            )
        )
        await sleep(30)
        await self.check_count_players(obj_message=obj_message)

    async def check_count_players(self, obj_message: UpdateMessage) -> None:
        """Проверка количества участников игры.
        Уведомление об остановке или старте игры.
        """
        chat_id = obj_message.chat_id
        game = await self.app.store.game.find_active_game(chat_id)
        if len(game.users) < 2:
            await self.app.game.service.deactivate_game(game)
            await self.app.bot.api.send_message(
                message=Message(
                    text=await self.app.store.game.get_phrase(
                        "absence_of_participants"
                    ),
                    chat_id=chat_id,
                )
            )
            self.logger.info("Game stopped: participants have not joined")
            return

        players_name: str = ""
        for game_user in game.users:
            players_name += (
                self.app.game.service.get_user_name(
                    username=game_user.user.username,
                    first_name=game_user.user.first_name,
                )
                + "\n"
            )

        await self.app.bot.api.send_message(
            message=Message(
                text=await self.app.store.game.get_phrase("game_started")
                + f"\nИгроки: \n{players_name}",
                chat_id=chat_id,
            )
        )
        await self.app.bot.api.send_message(
            message=Message(
                text=await self.app.store.game.get_phrase("session_info"),
                chat_id=chat_id,
            )
        )
        await self.app.bot.api.send_message(
            message=Message(
                text=await self.app.store.game.get_phrase("reply_awaited"),
                chat_id=chat_id,
                reply_markup=self.app.game.reply_markup.continue_further(),
            )
        )

    async def start_session(
        self, obj_callback: CallbackQuery
    ) -> Session | None:
        """Старт игровой сессии."""
        chat_id = obj_callback.chat_id
        game = await self.app.store.game.find_active_game(chat_id=chat_id)
        if game is None:
            self.logger.info("No active game found.")
            return None
        game_session = await self.app.game.service.create_session(
            game_id=game.id
        )
        stocks = await self.app.store.game.get_stocks()
        for stock in stocks:
            await self.app.game.service.create_session_stock(
                session_id=game_session.id, stock_id=stock.id
            )
        await self.get_quotes(chat_id=chat_id, session_id=game_session.id)
        session_number = game_session.number
        await self.app.bot.api.send_message(
            message=Message(
                text=f"🎯 Раунд {session_number}. Выберите 👇",
                chat_id=chat_id,
                reply_markup=await self.app.game.reply_markup.create_session(),
            )
        )

        return game_session

    async def stop(self, obj_message: UpdateMessage) -> None:
        """Остановка игры участником."""
        chat_id = obj_message.chat_id
        game = await self.app.store.game.find_active_game(chat_id=chat_id)
        if game is None:
            await self.app.bot.api.send_message(
                message=Message(
                    text=await self.app.store.game.get_phrase(
                        "game_is_already_stopped"
                    ),
                    chat_id=chat_id,
                )
            )
            return
        user_telegram_id = obj_message.from_.telegram_id
        if not self.app.game.service.is_participant(
            user_telegram_id=user_telegram_id, game=game
        ):
            reply_to_message_id = obj_message.message_id
            await self.app.bot.api.send_message(
                message=Message(
                    text="Не имеете прав останавливать игру. 🤖",
                    chat_id=chat_id,
                    reply_to_message_id=reply_to_message_id,
                )
            )
            return
        await self.get_game_result(chat_id=chat_id)
        await self.app.game.service.deactivate_game(game=game)
        await self.app.bot.api.send_message(
            message=Message(
                text=await self.app.store.game.get_phrase("game_stopped"),
                chat_id=chat_id,
            )
        )
        self.logger.info("Game stopped")

    async def get_quantity(self, obj_message: UpdateMessage) -> int | None:
        """Обработка числового ответа пользователя."""
        if not self.app.game.service.is_integer(obj_message.text):
            reply_to_message_id = obj_message.message_id
            await self.app.bot.api.send_message(
                message=Message(
                    text="Введено некорректное количество акций. 🤖",
                    chat_id=obj_message.chat_id,
                    reply_to_message_id=reply_to_message_id,
                )
            )
            return None
        return int(obj_message.text)

    async def start_exchange(self, obj_message: UpdateMessage) -> None:
        """Запуск торгов."""
        game = await self.app.store.game.find_active_game(obj_message.chat_id)
        if game is None:
            self.logger.info("No active game found.")
            return
        user_telegram_id = obj_message.from_.telegram_id
        if not self.app.game.service.is_participant(
            user_telegram_id=user_telegram_id, game=game
        ):
            self.logger.info("User is not a participant in the game.")
            return
        if obj_message.reply_to_message.text:
            stock_title, act = self.app.game.service.parse_stock_and_action(
                text=obj_message.reply_to_message.text
            ).split()
            if not stock_title or not act:
                self.logger.info("Couldn't parse stock_title and action")
                return
            quantity = await self.get_quantity(obj_message)
            if not quantity:
                self.logger.info("Couldn't parse quantity")
                return
            user = await self.app.store.user.get_user_by_telegram_id(
                telegram_id=user_telegram_id
            )
            game_user = await self.app.store.game.find_game_user(
                user_id=user.id, game_id=game.id
            )
            stock = await self.app.store.game.get_stock_by_title(
                stock_title=stock_title
            )
            price = await self.app.game.service.get_price(
                stock_id=stock.id, game_id=game.id
            )
            if act == self.app.bot.get_description(self.app.bot.BUY):
                await self.buy_stock(
                    obj_message=obj_message,
                    game_user=game_user,
                    quantity=quantity,
                    stock=stock,
                    price=price,
                )
            elif act == self.app.bot.get_description(self.app.bot.SELL):
                await self.sell_stock(
                    obj_message=obj_message,
                    game_user=game_user,
                    quantity=quantity,
                    stock=stock,
                    price=price,
                )

    async def buy_stock(
        self,
        obj_message: UpdateMessage,
        game_user: GameUser,
        quantity: int,
        stock: Stock,
        price: float,
    ) -> None:
        """Покупка акций."""
        reply_to_message_id = obj_message.message_id
        cash_balance = game_user.cash_balance
        new_cash_balance = self.app.game.service.decrease_cash_balance(
            quantity=quantity, cash_balance=cash_balance, price=price
        )
        if not new_cash_balance:
            await self.app.bot.api.send_message(
                message=Message(
                    text=f"💶 Ваш баланс: {cash_balance}у.е. "
                    f"Недостаточно средств для покупки {quantity} "
                    f"акций {stock.title} 📃 по цене {price}у.е.",
                    chat_id=obj_message.chat_id,
                    reply_to_message_id=reply_to_message_id,
                )
            )
            return
        game_user.cash_balance = new_cash_balance
        game_user = await self.app.store.game.save_game_user(
            game_user=game_user
        )
        await self.update_user_stock(
            game_user=game_user, stock=stock, quantity=quantity
        )
        await self.create_exchange(
            obj_message=obj_message,
            game_user=game_user,
            stock=stock,
            quantity=quantity,
            action=self.app.bot.BUY,
        )
        await self.app.bot.api.send_message(
            message=Message(
                text=f"Ваш баланс: {new_cash_balance}у.е. "
                f"Вы приобрели акции {stock.title} 📃 "
                f"в количестве: {quantity}шт.",
                chat_id=obj_message.chat_id,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def sell_stock(
        self,
        obj_message: UpdateMessage,
        game_user: GameUser,
        quantity: int,
        stock: Stock,
        price: float,
    ) -> None:
        """Продажа акций."""
        reply_to_message_id = obj_message.message_id
        user_stock = await self.app.store.game.find_user_stock(
            user_id=game_user.user_id,
            game_id=game_user.game_id,
            stock_id=stock.id,
        )
        if not user_stock:
            await self.app.bot.api.send_message(
                message=Message(
                    text="Операция не выполнена. "
                    f"Акции {stock.title} отсутствуют.",
                    chat_id=obj_message.chat_id,
                    reply_to_message_id=reply_to_message_id,
                )
            )
            return
        if user_stock.total_quantity < quantity:
            await self.app.bot.api.send_message(
                message=Message(
                    text=f"Недостаточно акций 📃 для выполнения этой сделки."
                    f"Акции {stock.title} доступны в количестве: "
                    f"{user_stock.total_quantity}шт.",
                    chat_id=obj_message.chat_id,
                    reply_to_message_id=reply_to_message_id,
                )
            )
            return
        user_stock.total_quantity -= quantity
        await self.app.store.game.save_user_stock(user_stock=user_stock)
        new_cash_balance = self.app.game.service.increase_cash_balance(
            quantity=quantity, cash_balance=game_user.cash_balance, price=price
        )
        game_user.cash_balance = new_cash_balance
        game_user = await self.app.store.game.save_game_user(
            game_user=game_user
        )
        await self.create_exchange(
            obj_message=obj_message,
            game_user=game_user,
            stock=stock,
            quantity=quantity,
            action=self.app.bot.SELL,
        )
        await self.app.bot.api.send_message(
            message=Message(
                text=f"Ваш баланс: {new_cash_balance}у.е. "
                f"Вы продали акции {stock.title} 📃 "
                f"в количестве: {quantity}шт.",
                chat_id=obj_message.chat_id,
                reply_to_message_id=reply_to_message_id,
            )
        )

    async def update_user_stock(
        self, game_user: GameUser, stock: Stock, quantity: int
    ) -> None:
        user_stock = await self.app.store.game.find_user_stock(
            user_id=game_user.user_id,
            game_id=game_user.game_id,
            stock_id=stock.id,
        )
        if not user_stock:
            await self.app.game.service.create_user_stock(
                user_id=game_user.user_id,
                game_id=game_user.game_id,
                stock_id=stock.id,
                total_quantity=quantity,
            )
        else:
            user_stock.total_quantity += quantity
            await self.app.store.game.save_user_stock(user_stock=user_stock)

    async def create_exchange(
        self,
        obj_message: UpdateMessage,
        game_user: GameUser,
        stock: Stock,
        quantity: int,
        action: str,
    ) -> None:
        session = await self.app.store.game.find_game_session(game_user.game_id)
        exchange = Exchange(
            user_id=game_user.user_id,
            session_id=session.id,
            chat_id=obj_message.chat_id,
            action=action,
            stock_id=stock.id,
            quantity=quantity,
        )
        await self.app.store.game.save_exchange(exchange)

    async def get_game_result(self, chat_id: str) -> None:
        game = await self.app.store.game.find_active_game(chat_id=chat_id)
        if not game:
            self.logger = getLogger("Active game not found")
            return
        users = {
            game_user.user_id: f"{self.app.game.service.get_user_name(
                game_user.user.username, game_user.user.first_name
            )
            }"
            for game_user in game.users
        }
        session = await self.app.store.game.find_game_session(game_id=game.id)
        stock_price = await self.app.store.game.find_stock_prices(
            session_id=session.id
        )
        user_balance = {
            game_user.user_id: game_user.cash_balance
            for game_user in game.users
        }
        users_stocks = await self.app.store.game.get_users_stocks(
            game_id=game.id
        )
        for user_stock in users_stocks:
            user_balance[user_stock.user_id] += (
                stock_price[user_stock.stock_id] * user_stock.total_quantity
            )
        session_number = session.number
        text = (
            "🎰 Суммарный денежный баланс игрока (в у.е.) после раунда "
            f"{session_number}:\n{
                '\n'.join(
                    [f"{users[key]}: {round(value, 2)}"
                     for key, value in user_balance.items()]
                )
                }"
        )
        await self.app.bot.api.send_message(
            message=Message(
                text=text,
                chat_id=chat_id,
            )
        )
