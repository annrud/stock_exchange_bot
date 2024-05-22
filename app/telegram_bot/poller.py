from asyncio import Queue, Task, create_task
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.web.app import Application


class Poller:
    def __init__(self, app: "Application", queue: Queue) -> None:
        self.app = app
        self.logger = getLogger("poller")
        self.is_running = False
        self._poll_task: Task | None = None
        self.queue = queue

    async def start(self) -> None:
        self.is_running = True
        self._poll_task = create_task(self.poll())

    async def stop(self) -> None:
        self.is_running = False
        await self._poll_task

    async def poll(self) -> None:
        while True:
            result = await self.app.bot.api.poll()
            if result:
                self.queue.put_nowait(result)
