import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

__all__ = ("setup_routes",)


def setup_routes(app: "Application"):
    from app.admin.views import AdminCurrentView, AdminLoginView

    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.current", AdminCurrentView)
