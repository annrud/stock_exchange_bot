from aiohttp.web_app import Application

__all__ = ("setup_routes",)


def setup_routes(app: Application):
    from app.admin.routes import setup_routes as admin_setup_routes
    from app.game.routes import setup_routes as game_setup_routes
    from app.user.routes import setup_routes as user_setup_routes

    admin_setup_routes(app)
    user_setup_routes(app)
    game_setup_routes(app)
