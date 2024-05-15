__all__ = ("User", "setup_user")

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.web.app import Application


class User:
    def __init__(self, app: "Application"):
        from app.user.service import UserService

        self.app = app
        self.service = UserService(app)


def setup_user(app: "Application"):
    app.user = User(app)
