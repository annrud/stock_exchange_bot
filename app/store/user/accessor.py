from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor

__all__ = ("UserAccessor",)

from app.user.models import UserModel


class UserAccessor(BaseAccessor):
    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> UserModel | None:
        async with AsyncSession(self.app.database.engine) as session:
            user = await session.execute(
                select(UserModel).filter(UserModel.telegram_id == telegram_id)
            )
            return user.scalar_one_or_none()

    async def save_user(self, user: UserModel) -> UserModel:
        async with AsyncSession(self.app.database.engine) as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        async with AsyncSession(self.app.database.engine) as session:
            user = await session.execute(
                select(UserModel).filter(UserModel.id == user_id)
            )
            return user.scalar_one_or_none()

    async def get_users(self) -> list[UserModel] | None:
        async with AsyncSession(self.app.database.engine) as session:
            result = await session.execute(select(UserModel))
            users = result.scalars().all()
            return users if users else None
