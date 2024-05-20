from typing import TYPE_CHECKING, Any

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.store.database.sqlalchemy_base import BaseModel

if TYPE_CHECKING:
    from app.web.app import Application

__all__ = ("Database",)


class Database:
    def __init__(self, app: "Application") -> None:
        self.app = app

        self.engine: AsyncEngine | None = None
        self._db: type[DeclarativeBase] = BaseModel
        self.session: async_sessionmaker[AsyncSession] | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        self.engine = create_async_engine(
            URL.create(
                drivername="postgresql+asyncpg",
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                host=self.app.config.database.host,
                database=self.app.config.database.database,
            ),
            echo=True,
        )
        self.session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self.session:
            async with self.session() as session:
                await session.close()
        if self.engine:
            await self.engine.dispose()
