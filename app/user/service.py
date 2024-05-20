from logging import getLogger
from typing import TYPE_CHECKING

from app.user.models import UserModel

if TYPE_CHECKING:
    from app.web.app import Application

__all__ = ("UserService",)


class UserService:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")

    async def create_user(self, **kwargs) -> UserModel | None:
        data = kwargs.get("data")
        if data is None:
            self.logger.info("User is None")
            return None
        user = await self.app.store.user.get_user_by_telegram_id(
            data.telegram_id
        )
        if user is None:
            user = await self.app.store.user.save_user(
                UserModel(
                    telegram_id=data.telegram_id,
                    first_name=data.first_name,
                    last_name=data.last_name,
                    username=data.username,
                )
            )
        return user
