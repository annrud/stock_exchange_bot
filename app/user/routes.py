from typing import TYPE_CHECKING

from app.user.views import UserListView

if TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/users", UserListView)
