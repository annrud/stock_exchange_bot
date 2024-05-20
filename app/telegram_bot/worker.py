from asyncio import Queue, Task, create_task
from logging import getLogger
from typing import TYPE_CHECKING

from app.telegram_bot.utils import parse_callback_query, parse_message

if TYPE_CHECKING:
    from app.web.app import Application


class Worker:
    def __init__(
        self, app: "Application", queue: Queue, concurrent_workers: int
    ):
        self.app = app
        self.logger = getLogger("worker")
        self.concurrent_workers = concurrent_workers
        self.queue = queue
        self._tasks: list[Task] = []

    async def handle_update(self, upd):
        if "message" in upd:
            update = parse_message(upd)
            await self.app.bot.msg_manager.handle_update_message(update)
        if "callback_query" in upd:
            update = parse_callback_query(upd)
            await self.app.bot.clb_manager.handle_update_callback(update)

    async def _worker(self):
        while True:
            upd = await self.queue.get()
            try:
                self._handle_task = await create_task(self.handle_update(upd))
                self._tasks.append(self._handle_task)
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [
            create_task(self._worker()) for _ in range(self.concurrent_workers)
        ]

    async def stop(self):
        await self.queue.join()
        for task in self._tasks:
            await task
