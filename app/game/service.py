import random
from datetime import datetime
from logging import getLogger
from typing import TYPE_CHECKING

from app.game.models import GameModel, GameUser, Session, SessionStock
from app.telegram_bot.dataclasses import (
    From,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

if TYPE_CHECKING:
    from app.web.app import Application

__all__ = ("GameService", "ReplyMarkupService")


class ReplyMarkupService:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("MessageService")

    def get_reply_markup(
        self, inline_buttons: list[InlineKeyboardButton]
    ) -> dict[str, InlineKeyboardMarkup]:
        inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[])
        inline_keyboard_markup.inline_keyboard.append(inline_buttons)

        return {
            "inline_keyboard": [
                [button.to_dict() for button in row]
                for row in inline_keyboard_markup.inline_keyboard
            ]
        }

    def create_start_reply_markup(
        self,
    ) -> dict[str, InlineKeyboardMarkup] | None:
        inline_button = [
            InlineKeyboardButton(
                text="Присоединиться к игре",
                callback_data="Join_the_game",
            )
        ]
        return self.get_reply_markup(inline_button)

    def create_start_session_reply_markup(
        self, players_telegram_id: list[int]
    ) -> dict[str, InlineKeyboardMarkup] | None:
        inline_button = [
            InlineKeyboardButton(
                text="Купить",
                callback_data=f"Buy_{players_telegram_id}",
            ),
            InlineKeyboardButton(
                text="Продать",
                callback_data=f"Sell_{players_telegram_id}",
            ),
            InlineKeyboardButton(
                text="Пропустить ход",
                callback_data=f"Skip_turn_{players_telegram_id}",
            ),
        ]
        return self.get_reply_markup(inline_button)


class GameService:
    DEFAULT_CASH_BALANCE: float = 100.0

    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("GameService")

    async def create_game(self, **kwargs) -> GameModel | None:
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
        user = await self.app.user.service.create_user(data=data)
        game_user = await self.app.store.game.find_game_user(
            game_id=game.id, user_id=user.id
        )
        if game_user is None:
            game_user = GameUser(
                user_id=user.id,
                game_id=game.id,
                cash_balance=self.DEFAULT_CASH_BALANCE,
            )
            await self.app.store.game.add_game_user(game_user=game_user)

    async def deactivate_game(self, game: GameModel) -> None:
        game.is_active = False
        await self.app.store.game.save_game(game)

    async def create_session(self, game_id: int) -> Session:
        game_session = await self.app.store.game.find_game_session(
            game_id=game_id
        )
        number = game_session.number + 1 if game_session is Session else 1
        new_game_session = Session(number=number, game_id=game_id)
        return await self.app.store.game.save_game_session(
            game_session=new_game_session
        )

    async def create_session_stock(
        self, session_id: int, stock_id: int
    ) -> SessionStock:
        price = round(random.uniform(10, 100), 2)

        return await self.app.store.game.save_session_stock(
            session_stock=SessionStock(
                session_id=session_id, stock_id=stock_id, price=price
            )
        )

    async def get_stock_price(
        self, chat_id: str, session_id: int | None = None
    ) -> str:
        session_stocks = await self.get_session_stock(chat_id, session_id)
        stock_price = ""
        for session_stock in session_stocks:
            title = session_stock.stock.title
            price = session_stock.price
            stock_price += f"{title}: {price}\n"
        return stock_price

    async def get_session_stock(
        self, chat_id: str, session_id: int | None = None
    ) -> list[SessionStock] | None:
        if session_id is None:
            game = await self.app.store.game.find_active_game(chat_id=chat_id)
            if game is None:
                return None
            game_session = await self.app.store.game.find_game_session(
                game_id=game.id
            )
            if game_session is None:
                return None
            session_id = game_session.session_id

        return await self.app.store.game.find_session_stock_by_session_id(
            session_id=session_id
        )
