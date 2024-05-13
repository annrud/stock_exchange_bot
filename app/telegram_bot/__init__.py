__all__ = ("Bot", "setup_bot")


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.web.app import Application


class Bot:
    def __init__(self, app: "Application"):
        from app.telegram_bot.accessor import TelegramApiAccessor
        from app.telegram_bot.manager import BotManager

        self.app = app
        self.api = TelegramApiAccessor(app)
        self.manager = BotManager(app)


def setup_bot(app: "Application"):
    app.bot = Bot(app)
