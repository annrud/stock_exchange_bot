from aiohttp_apispec import docs, querystring_schema, response_schema

from app.game.models import Exchange
from app.game.schemas import ExchangeListSchema, ExchangeSchema, UserIdSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response

__all__ = ("ExchangeListView",)


class ExchangeListView(AuthRequiredMixin, View):
    @docs(
        tags=["exchange"],
        summary="Get exchange logs",
        description="Get exchange logs from database",
    )
    @querystring_schema(UserIdSchema)
    @response_schema(ExchangeListSchema, 200)
    async def get(self):
        user_id = self.get_user_id_from_query()
        exchanges = await self.get_exchanges_by_user_id(user_id)
        raw_exchanges = [
            ExchangeSchema().dump(exchange) for exchange in exchanges
        ]
        return json_response(data={"exchanges": raw_exchanges})

    async def get_exchanges_by_user_id(
        self, user_id: int | None
    ) -> list[Exchange]:
        if user_id is None:
            return await self.store.game.get_exchanges()
        return await self.store.game.find_exchanges(user_id=user_id)

    def get_user_id_from_query(self) -> int | None:
        user_id = self.request.query.get("user_id")
        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None
