from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game.models import Game, GameUser, Phrase
from app.telegram_bot.dataclasses import From
from app.user.models import User

if TYPE_CHECKING:
    from app.web.app import Application

__all__ = ("GameAccessor",)


class GameAccessor(BaseAccessor):
    DEFAULT_CASH_BALANCE: float = 100.0

    async def connect(self, app: "Application", *args, **kwargs) -> None:
        async with AsyncSession(self.app.database.engine) as session:
            chat_id = kwargs.get("chat_id")
            data = kwargs.get("data")
            if data is None:
                self.logger.info("User is None")
                return
            game = Game(
                chat_id=chat_id, is_active=True, created_at=datetime.now()
            )
            session.add(game)
            await session.commit()
            await self.add_user_to_game(chat_id, data)
            self.logger.info("Created new game")

    async def get_active_game(self, chat_id: str) -> Game | None:
        async with AsyncSession(self.app.database.engine) as session:
            game = await session.execute(
                select(Game)
                .filter(Game.chat_id == chat_id, Game.is_active.is_(True))
                .order_by(Game.id.desc())
                .limit(1)
            )
            return game.scalar_one_or_none()

    async def add_user_to_game(self, chat_id: str, data: From) -> None:
        async with AsyncSession(self.app.database.engine) as session:
            user: User = await self.app.store.user.create_user(session, data)
            game: Game | None = await self.get_active_game(chat_id)
            if game:
                existing_game_user = await session.execute(
                    select(GameUser).filter(
                        GameUser.user_id == user.id, GameUser.game_id == game.id
                    )
                )
                existing_game_user = existing_game_user.scalar_one_or_none()
                if existing_game_user:
                    return

                game_user = GameUser(
                    user_id=user.id,
                    game_id=game.id,
                    cash_balance=self.DEFAULT_CASH_BALANCE,
                )
                session.add(game_user)
                await session.commit()

    async def get_users_id_from_game(self, chat_id: str) -> list[int]:
        async with AsyncSession(self.app.database.engine) as session:
            current_game = await self.get_active_game(chat_id)
            if current_game:
                users_id = await session.execute(
                    select(GameUser.user_id).filter(
                        GameUser.game_id == current_game.id
                    )
                )
                return users_id.scalars().all()
            return []

    async def get_phrase(self, key: str) -> str | None:
        async with AsyncSession(self.app.database.engine) as session:
            phrase = await session.execute(
                select(Phrase.phrase).filter(Phrase.key == key)
            )
            return phrase.scalar_one_or_none()

    async def deactivate_the_game(self, chat_id: str) -> None:
        async with AsyncSession(self.app.database.engine) as session:
            game = await self.get_active_game(chat_id)
            if game:
                await session.execute(
                    update(Game)
                    .filter(Game.id == game.id)
                    .values(is_active=False)
                )
                await session.commit()
