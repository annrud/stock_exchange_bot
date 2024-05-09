import json
import typing
from urllib.parse import urlencode, urljoin

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.telegram_api.dataclasses import CallbackQuery, Message
from app.store.telegram_api.poller import Poller
from app.store.telegram_api.utils import parse_callback_query, parse_message

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TelegramApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.host: str | None = self.app.config.bot.get_token_path
        self.poller: Poller | None = None
        self.offset: int | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        self.poller.start()

    async def disconnect(self, app: "Application") -> None:
        if self.session:
            await self.session.close()

        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        host = f"{host}/method"
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def poll(self):
        async with self.session.get(
                self._build_query(
                    host=self.host,
                    method="getUpdates",
                    params={
                        "offset": self.offset,
                        "timeout": 30,
                        "allowed_updates": ["message", "callback_query"],
                    },
                )
        ) as response:
            data = await response.json()
            self.logger.info(data)
            results = data.get("result", [])
            if results:
                result = results[-1]
                self.offset = result.get("update_id") + 1
                if "message" in result:
                    update = parse_message(result)
                    await self.app.store.bots_manager.handler_update_message(
                        update
                    )

                if "callback_query" in result:
                    update = parse_callback_query(result)
                    await self.app.store.bots_manager.handler_update_callback_query(
                        update
                    )

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                host=self.host,
                method="sendMessage",
                params={
                    "chat_id": message.chat_id,
                    "text": message.text,
                    "reply_markup": json.dumps(message.reply_markup),
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)

    async def answer_callback_query(
            self, callback_query: CallbackQuery
    ) -> None:
        async with self.session.get(
            self._build_query(
                host=self.host,
                method="answerCallbackQuery",
                params={
                    "callback_query_id": callback_query.callback_id,
                    "text": f"@{callback_query.from_.username} "
                            "присоединился(ась) к игре.",
                    "cache_time": 60,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)
