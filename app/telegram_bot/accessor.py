import json
from asyncio import Queue
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urljoin

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.telegram_bot.dataclasses import CallbackQuery, From, Message
from app.telegram_bot.poller import Poller
from app.telegram_bot.worker import Worker

if TYPE_CHECKING:
    from app.web.app import Application

__all_ = ("TelegramApiAccessor",)


class TelegramApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.session: ClientSession | None = None
        self.host: str | None = self.app.config.bot.get_token_path()
        self.queue = Queue()
        self.poller: Poller | None = None
        self.offset: int | None = None
        self.worker: Worker | None = None

    async def connect(self, app: "Application") -> None:
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        self.poller = Poller(app, self.queue)
        self.worker = Worker(app, self.queue, 2)
        self.poller.start()
        self.logger.info("start polling")

        await self.worker.start()
        self.logger.info("start worker")

    async def disconnect(self, app: "Application") -> None:
        if self.session:
            await self.session.close()

        if self.poller:
            await self.poller.stop()

        if self.worker:
            await self.worker.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        host = f"{host}/method"
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def poll(self) -> list | None:
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
                return result
            return None

    async def send_message(self, message: Message) -> None:
        params = {
            "chat_id": message.chat_id,
            "text": message.text,
        }
        if message.reply_markup:
            params["reply_markup"] = json.dumps(message.reply_markup)
        if message.reply_to_message_id:
            params["reply_to_message_id"] = message.reply_to_message_id
        async with self.session.get(
            self._build_query(
                host=self.host,
                method="sendMessage",
                params=params,
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)

    async def answer_callback_query(
        self, callback_query: CallbackQuery, player_name: str, text: str
    ) -> None:
        async with self.session.get(
            self._build_query(
                host=self.host,
                method="answerCallbackQuery",
                params={
                    "callback_query_id": callback_query.callback_id,
                    "text": f"{player_name} {text}",
                    "cache_time": 30,
                },
            )
        ) as response:
            data = await response.json()
            self.logger.info(data)

    async def get_me(self) -> From | None:
        async with self.session.get(
            self._build_query(host=self.host, method="getme", params={})
        ) as response:
            data = await response.json()
            self.logger.info(data)
            result = data.get("result", [])
            if result:
                return From(
                    telegram_id=result["id"],
                    first_name=result["first_name"],
                    username=result["username"],
                )
            return None
