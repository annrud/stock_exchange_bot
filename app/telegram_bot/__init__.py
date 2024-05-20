__all__ = ("Bot", "setup_bot")


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.web.app import Application


class Bot:
    BUY = "buy"
    SELL = "sell"
    SKIP = "skip"
    CONTINUE = "continue"

    def __init__(self, app: "Application"):
        from app.telegram_bot.accessor import TelegramApiAccessor
        from app.telegram_bot.callback_manager import CallbackManager
        from app.telegram_bot.message_manager import MessageManager

        self.app = app
        self.api = TelegramApiAccessor(app)
        self.msg_manager = MessageManager(app)
        self.clb_manager = CallbackManager(app)

    @classmethod
    def get_description(cls, action):
        descriptions = {
            cls.BUY: "купить",
            cls.SELL: "продать",
        }
        return descriptions.get(action, "")


def setup_bot(app: "Application"):
    app.bot = Bot(app)
