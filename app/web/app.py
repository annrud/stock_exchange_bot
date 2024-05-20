from pathlib import Path

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.admin.models import AdminModel
from app.store import Store, setup_store
from app.store.database.database import Database

from .config import Config, setup_config
from .logger import setup_logging
from .middlewares import setup_middlewares
from .routes import setup_routes

__all__ = ("Application", "Request", "View", "setup_app")

from ..game import Game, setup_game
from ..telegram_bot import Bot, setup_bot
from ..user import User, setup_user


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database | None = None
    bot: Bot | None = None
    game: Game | None = None
    user: User | None = None


class Request(AiohttpRequest):
    admin: AdminModel | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self) -> Database:
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: Path) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    session_setup(app, EncryptedCookieStorage(app.config.session.key))
    setup_routes(app)
    setup_aiohttp_apispec(
        app,
        title="Stock Exchange Telegram Bot",
        url="/docs/swagger.json",
        swagger_path="/docs",
    )
    setup_middlewares(app)
    setup_bot(app)
    setup_store(app)
    setup_game(app)
    setup_user(app)

    return app
