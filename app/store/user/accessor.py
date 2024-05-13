from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor

__all__ = ("UserAccessor",)

from app.telegram_bot.dataclasses import From
from app.user.models import User


class UserAccessor(BaseAccessor):
    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        async with AsyncSession(self.app.database.engine) as session:
            user = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return user.scalars().first()

    async def create_user(self, session: AsyncSession, data: From) -> User:
        existing_user = await self.get_user_by_telegram_id(data.telegram_id)
        if existing_user:
            return existing_user
        user = User(
            telegram_id=data.telegram_id,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
