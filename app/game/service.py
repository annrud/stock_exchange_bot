import random
import re
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING

from app.game.models import (
    GameModel,
    GameUser,
    Session,
    SessionStock,
    UserStock,
)
from app.telegram_bot.dataclasses import (
    ForceReply,
    From,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

if TYPE_CHECKING:
    from app.web.app import Application

__all__ = ("GameService", "ReplyMarkupService")


class ReplyMarkupService:
    """Класс для управления сообщениями и создания инлайн-клавиатур."""

    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("ReplyMarkupService")

    @staticmethod
    def _get_reply_markup(
        inline_buttons: list[InlineKeyboardButton],
    ) -> dict[str, InlineKeyboardMarkup]:
        """Формирование инлайн-клавиатуры."""
        inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[])

        inline_keyboard_markup.inline_keyboard = [
            inline_buttons[i : i + 2] for i in range(0, len(inline_buttons), 2)
        ]

        return {
            "inline_keyboard": [
                [button.to_dict() for button in row]
                for row in inline_keyboard_markup.inline_keyboard
            ]
        }

    def create_start(
        self,
    ) -> dict[str, InlineKeyboardMarkup] | None:
        """Создание кнопки для присоединения к игре."""
        inline_button = [
            InlineKeyboardButton(
                text="Присоединиться к игре ☝",
                callback_data="Join_the_game",
            )
        ]
        return self._get_reply_markup(inline_button)

    async def create_session(self) -> dict[str, InlineKeyboardMarkup] | None:
        """Создание игровых кнопок."""
        stocks = await self.app.store.game.get_stocks()
        inline_buttons = []
        for stock in stocks:
            inline_buttons.append(
                InlineKeyboardButton(
                    text=f"Купить {stock.title}",
                    callback_data=f"{self.app.bot.BUY}_{stock.title}",
                )
            )
            inline_buttons.append(
                InlineKeyboardButton(
                    text=f"Продать {stock.title}",
                    callback_data=f"{self.app.bot.SELL}_{stock.title}",
                )
            )
        inline_buttons.append(
            InlineKeyboardButton(
                text="Пропустить ход",
                callback_data=self.app.bot.SKIP,
            )
        )
        return self._get_reply_markup(inline_buttons)

    @staticmethod
    def get_force_reply_markup(placeholder_text: str) -> dict:
        """Создание интерфейса ответа пользователя на вопросы от бота."""
        force_reply = ForceReply(
            force_reply=True,
            input_field_placeholder=placeholder_text,
            selective=True,
        )
        return force_reply.to_dict()

    def continue_further(self) -> dict[str, InlineKeyboardMarkup]:
        """Создание кнопки 'Продолжить'."""
        inline_buttons = [
            InlineKeyboardButton(
                text="Продолжить",
                callback_data=self.app.bot.CONTINUE,
            )
        ]
        return self._get_reply_markup(inline_buttons)


class GameService:
    """Класс предоставляет методы для управления игровым процессом."""

    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("GameService")

    async def create_game(self, **kwargs) -> GameModel | None:
        """Создание игры."""
        chat_id = kwargs.get("chat_id")
        data = kwargs.get("data")
        if data is None:
            self.logger.info("User is None")
            return None

        game = GameModel(
            chat_id=chat_id, is_active=True, created_at=datetime.now()
        )
        return await self.app.store.game.save_game(game=game)

    async def join_user_to_game(self, game: GameModel, data: From) -> None:
        """Добавление пользователя в игру."""
        user = await self.app.user.service.create_user(data=data)
        game_user = await self.app.store.game.find_game_user(
            user_id=user.id, game_id=game.id
        )
        if game_user is None:
            game_user = GameUser(
                user_id=user.id,
                game_id=game.id,
                cash_balance=self.app.game.DEFAULT_CASH_BALANCE,
            )
            await self.app.store.game.save_game_user(game_user=game_user)

    async def deactivate_game(self, game: GameModel) -> None:
        """Деактивация игры."""
        game.is_active = False
        await self.app.store.game.save_game(game)

    async def create_session(self, game_id: int) -> Session:
        """Создание игровой сессии."""
        game_session = await self.app.store.game.find_game_session(
            game_id=game_id
        )
        number = game_session.number + 1 if game_session else 1
        new_game_session = Session(number=number, game_id=game_id)
        return await self.app.store.game.save_game_session(
            game_session=new_game_session
        )

    async def create_session_stock(
        self, session_id: int, stock_id: int
    ) -> SessionStock:
        """Создание записей сессия-акция-прайс."""
        price = round(random.uniform(10, 50), 2)

        return await self.app.store.game.save_session_stock(
            session_stock=SessionStock(
                session_id=session_id, stock_id=stock_id, price=price
            )
        )

    async def get_str_stocks_price(
        self, chat_id: str, session_id: int | None = None
    ) -> str | None:
        """Формирование строки с наименованием акций и прайсом."""
        session_stocks = await self.get_session_stock(chat_id, session_id)
        if session_stocks is None:
            return None
        str_stocks_price = ""
        for session_stock in session_stocks:
            title = session_stock.stock.title
            price = session_stock.price
            str_stocks_price += f"{title}: {price}\n"
        return str_stocks_price

    async def get_str_user_stock_quantity(
        self, game_id: int, user_id: int
    ) -> str | None:
        """Формирование строки с наименованием акций и количеством."""
        user_stocks = await self.app.store.game.find_user_stock_by_user_id(
            game_id=game_id, user_id=user_id
        )
        if user_stocks is None:
            return None
        str_stock_quantity = ""
        for user_stock in user_stocks:
            title = user_stock.stock.title
            quantity = user_stock.total_quantity
            str_stock_quantity += f"{title}: {quantity}шт.\n"
        return str_stock_quantity

    async def get_session_stock(
        self, chat_id: str, session_id: int | None = None
    ) -> list[SessionStock] | None:
        """Получение списка записей сессия-акция-прайс."""
        if session_id is None:
            game = await self.app.store.game.find_active_game(chat_id=chat_id)
            if game is None:
                return None
            game_session = await self.app.store.game.find_game_session(
                game_id=game.id
            )
            if game_session is None:
                return None
            session_id = game_session.id

        return await self.app.store.game.find_session_stocks_by_session_id(
            session_id=session_id
        )

    @staticmethod
    def get_user_name(username: str, first_name: str) -> str:
        """Получение имени игрока."""
        return f"@{username}" if username else f"{first_name}"

    @staticmethod
    def is_participant(user_telegram_id: int, game: GameModel) -> bool:
        """Проверяет, является ли пользователь участником игры."""
        players_telegram_ids = (
            game_user.user.telegram_id for game_user in game.users
        )
        return user_telegram_id in players_telegram_ids

    @staticmethod
    def is_integer(answer: str) -> bool:
        """Проверяет, является ли ответ числом."""
        return bool(re.match(r"^ *\d+ *$", answer))

    @staticmethod
    def parse_stock_and_action(text: str) -> str | None:
        """Парсит строку с вопросом бота,
        возвращает текст с названием акции и
        действием: купить или продать.
        """
        pattern = r"сколько акций (.*?)\?"
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return None

    async def get_price(self, stock_id: int, game_id: int) -> float:
        """Получение текущей стоимости акции."""
        session = await self.app.store.game.find_game_session(game_id=game_id)
        session_stock = await self.app.store.game.find_session_stock(
            session_id=session.id, stock_id=stock_id
        )
        return session_stock.price

    @staticmethod
    def decrease_cash_balance(
        price: float, cash_balance: float, quantity: int
    ) -> float | None:
        """Уменьшение денежного баланса игрока."""
        result = round(cash_balance - quantity * price, 2)
        return result if result >= 0 else None

    @staticmethod
    def increase_cash_balance(
        price: float, cash_balance: float, quantity: int
    ) -> float | None:
        """Увеличение денежного баланса игрока."""
        return round(cash_balance + quantity * price, 2)

    async def create_user_stock(
        self, user_id: int, game_id: int, stock_id: int, total_quantity: int
    ) -> None:
        user_stock = UserStock(
            user_id=user_id,
            game_id=game_id,
            stock_id=stock_id,
            total_quantity=total_quantity,
        )
        await self.app.store.game.save_user_stock(user_stock=user_stock)
