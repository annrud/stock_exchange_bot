import asyncio
from asyncio import Future, Task
from logging import getLogger

from app.telegram_bot import Bot


class Poller:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.logger = getLogger("poller")
        self.is_running = False
        self.poll_task: Task | None = None

    def _done_callback(self, result: Future) -> None:
        if result.exception():
            self.logger.exception(
                "poller stopped with exception", exc_info=result.exception()
            )
        if self.is_running:
            self.start()

    def start(self) -> None:
        self.is_running = True

        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)

    async def stop(self) -> None:
        self.is_running = False

        await self.poll_task

    async def poll(self) -> None:
        await self.bot.api.poll()
