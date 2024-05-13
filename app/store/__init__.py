from app.store.database.database import Database

__all__ = ("Store", "setup_store")

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.game.accessor import GameAccessor
        from app.store.user.accessor import UserAccessor

        self.app = app
        self.admins = AdminAccessor(app)
        self.user = UserAccessor(app)
        self.game = GameAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
