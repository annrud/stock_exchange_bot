from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.store.admin.accessor import validate_password
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

__all__ = (
    "AdminCurrentView",
    "AdminLoginView",
)


class AdminLoginView(View):
    @docs(
        tags=["admin"],
        summary="Admin authentication",
        description="Authentication by email and password",
    )
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email: str = self.data["email"]
        admin = await self.store.admins.get_by_email(email)

        if admin is None:
            raise HTTPForbidden(reason="there is no admin with this email")
        if not validate_password(self.data["password"], admin.password):
            raise HTTPForbidden(reason="invalid password")

        session = await new_session(self.request)
        raw_admin = AdminSchema().dump(admin)
        session["admin"] = raw_admin
        return json_response(data=raw_admin)


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="Get current admin",
        description="Get current admin from request",
    )
    @response_schema(AdminSchema, 200)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
