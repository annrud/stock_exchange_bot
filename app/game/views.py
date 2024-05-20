from aiohttp_apispec import docs, response_schema

from app.game.schemas import ExchangeListSchema, ExchangeSchema
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
    @response_schema(ExchangeListSchema, 200)
    async def get(self):
        exchanges = await self.store.game.get_exchanges()
        raw_exchanges = [
            ExchangeSchema().dump(exchange) for exchange in exchanges
        ]
        return json_response(data={"exchanges": raw_exchanges})
