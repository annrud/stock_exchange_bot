from aiohttp_apispec import docs, response_schema

from app.user.schemas import UserListSchema, UserSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

__all__ = ("UserListView",)


class UserListView(AuthRequiredMixin, View):
    @docs(
        tags=["user"],
        summary="Get users",
        description="Get all users from database",
    )
    @response_schema(UserListSchema, 200)
    async def get(self):
        users = await self.store.user.get_users()
        raw_users = [UserSchema().dump(user) for user in users]
        return json_response(data={"users": raw_users})
