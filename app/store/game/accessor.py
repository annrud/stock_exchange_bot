import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    Exchange,
    GameModel,
    GameUser,
    Phrase,
    Session,
    SessionStock,
    Stock,
    UserStock,
)

__all__ = ("GameAccessor",)


class GameAccessor(BaseAccessor):
    async def save_game(self, game: GameModel) -> GameModel:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(game)
            await session.commit()
            await session.refresh(game)
            return game

    async def find_active_game(self, chat_id: str) -> GameModel | None:
        async with AsyncSession(self.app.database.engine) as session:
            game = await session.execute(
                select(GameModel)
                .filter(
                    GameModel.chat_id == chat_id, GameModel.is_active.is_(True)
                )
                .options(
                    selectinload(GameModel.users).selectinload(GameUser.user)
                )
                .order_by(GameModel.id.desc())
                .limit(1)
            )
            return game.scalar_one_or_none()

    async def save_game_user(self, game_user: GameUser) -> GameUser:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(game_user)
            await session.commit()
            await session.refresh(game_user)
            return game_user

    async def find_game_user(
        self, game_id: int, user_id: int
    ) -> GameUser | None:
        async with AsyncSession(self.app.database.engine) as session:
            game_user = await session.execute(
                select(GameUser).filter(
                    GameUser.game_id == game_id, GameUser.user_id == user_id
                )
            )
            return game_user.scalar_one_or_none()

    async def find_game_session(self, game_id: int) -> Session | None:
        async with AsyncSession(self.app.database.engine) as session:
            result = await session.execute(
                select(Session)
                .filter(Session.game_id == game_id)
                .order_by(Session.id.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

    async def save_game_session(self, game_session: Session) -> Session:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(game_session)
            await session.commit()
            await session.refresh(game_session)
            return game_session

    async def save_session_stock(
        self, session_stock: SessionStock
    ) -> SessionStock:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(session_stock)
            await session.commit()
            await session.refresh(session_stock)
            return session_stock

    async def find_session_stocks_by_session_id(
        self, session_id: int
    ) -> list[SessionStock]:
        async with AsyncSession(self.app.database.engine) as session:
            result = await session.execute(
                select(SessionStock).filter(
                    SessionStock.session_id == session_id
                ),
            )
            return result.scalars().all()

    async def find_stock_prices(self, session_id: int) -> {}:
        async with AsyncSession(self.app.database.engine) as session:
            query = sqlalchemy.text(
                "SELECT stock_id, price FROM session_stock "
                "WHERE session_id = :session_id"
            )
            result_set = await session.execute(
                query, {"session_id": session_id}
            )

            return {
                _item.stock_id: _item.price
                for _item in result_set.mappings().all()
            }

    async def find_session_stock(
        self, session_id: int, stock_id: int
    ) -> SessionStock | None:
        async with AsyncSession(self.app.database.engine) as session:
            session_stock = await session.execute(
                select(SessionStock).filter(
                    SessionStock.session_id == session_id,
                    SessionStock.stock_id == stock_id,
                )
            )
            return session_stock.scalar_one_or_none()

    async def save_user_stock(self, user_stock: UserStock) -> UserStock:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(user_stock)
            await session.commit()
            await session.refresh(user_stock)
            return user_stock

    async def find_user_stock(
        self, game_id: int, user_id: int, stock_id: int
    ) -> UserStock | None:
        async with AsyncSession(self.app.database.engine) as session:
            user_stock = await session.execute(
                select(UserStock).filter(
                    UserStock.user_id == user_id,
                    UserStock.game_id == game_id,
                    UserStock.stock_id == stock_id,
                )
            )
            return user_stock.scalar_one_or_none()

    async def get_users_stocks(self, game_id: int) -> list[UserStock]:
        async with AsyncSession(self.app.database.engine) as session:
            users_stocks = await session.execute(
                select(UserStock).filter(UserStock.game_id == game_id)
            )
            return users_stocks.scalars().all()

    async def find_user_stock_by_user_id(
        self, game_id: int, user_id: int
    ) -> list[UserStock]:
        async with AsyncSession(self.app.database.engine) as session:
            users_stocks = await session.execute(
                select(UserStock).filter(
                    UserStock.game_id == game_id, UserStock.user_id == user_id
                )
            )
            return users_stocks.scalars().all()

    async def get_phrase(self, key: str) -> str | None:
        async with AsyncSession(self.app.database.engine) as session:
            phrase = await session.execute(
                select(Phrase.phrase).filter(Phrase.key == key)
            )
            return phrase.scalar_one_or_none()

    async def get_stock_by_title(self, stock_title: str) -> Stock | None:
        async with AsyncSession(self.app.database.engine) as session:
            stock = await session.execute(
                select(Stock).filter(Stock.title == stock_title)
            )
            return stock.scalar_one_or_none()

    async def get_stocks(self) -> list[Stock]:
        async with AsyncSession(self.app.database.engine) as session:
            stocks = await session.execute(select(Stock))
            return stocks.scalars().all()

    async def save_exchange(self, exchange: Exchange) -> None:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(exchange)
            await session.commit()

    async def get_exchanges(self) -> list[Exchange] | None:
        async with AsyncSession(self.app.database.engine) as session:
            result = await session.execute(select(Exchange))
            return result.scalars().all()
