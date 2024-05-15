__all__ = ("Game", "setup_game")

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.web.app import Application


class Game:
    def __init__(self, app: "Application"):
        from app.game.service import GameService, ReplyMarkupService

        self.app = app
        self.service = GameService(app)
        self.reply_markup_service = ReplyMarkupService(app)


def setup_game(app: "Application"):
    app.game = Game(app)
