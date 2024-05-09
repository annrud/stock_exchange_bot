from typing import TYPE_CHECKING

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

if TYPE_CHECKING:
    from app.web.app import Application


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        self.app = app
        await self.create_admin(
            email=self.app.config.admin.email,
            password=self.app.config.admin.password,
        )

    async def get_by_email(self, email: str) -> AdminModel | None:
        async with AsyncSession(self.app.database.engine) as session:
            admin = await session.execute(
                select(AdminModel).filter(AdminModel.email == email)
            )
            return admin.scalar_one_or_none()

    async def create_admin(self, email: str, password: str) -> AdminModel:
        existing_admin = await self.get_by_email(email)
        if existing_admin:
            return existing_admin
        admin = AdminModel(email=email, password=hash_password(password))
        async with AsyncSession(self.app.database.engine) as session:
            session.add(admin)
            await session.commit()
        return admin
