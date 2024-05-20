from typing import TYPE_CHECKING

from app.game.views import ExchangeListView

if TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/exchange_logs", ExchangeListView)
