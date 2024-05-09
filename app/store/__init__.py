from app.store.database.database import Database

__all__ = ("Store", "setup_store")

import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.bot.manager import BotManager
        from app.store.telegram_api.accessor import TelegramApiAccessor
        from app.user.accessor import UserAccessor

        self.app = app
        self.telegram_api = TelegramApiAccessor(app)
        self.admins = AdminAccessor(app)
        self.bots_manager = BotManager(app)
        self.user = UserAccessor(self)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
