import asyncio
import struct
from datetime import datetime

from wizmsg import DATA_START_MAGIC, LARGE_DATA_MAGIC, ByteInterface, Server


class Session:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, server: Server):
        self.reader = reader
        self.writer = writer
        self.server = server

        self.start_time = datetime.now()
        self.id: int

        self.alive: bool = True

        self.heartbeat_task: asyncio.Task | None = None
        self.process_loop_task: asyncio.Task | None = None

    async def start(self):
        """
        accept session, start heartbeat, start process loop
        """
        await self.accept_session()
        self.heartbeat_task = asyncio.create_task(self.heartbeat())
        self.process_loop_task = asyncio.create_task(self.process_loop())

    async def stop(self):
        """
        stop session and tasks
        """
        self.alive = False
        self.heartbeat_task.cancel()
        self.process_loop_task.cancel()

    async def accept_session(self):
        pass

    # https://kronos-project.github.io/grimoire/internals/protocol/sessions.html#heartbeat
    async def heartbeat(self):
        """
        Send Keep alive every 60 seconds, wait for response, close if none after 60 seconds
        """
        pass

    async def process_loop(self):
        while self.alive:
            magic_and_size = await self.reader.read(4)

            magic, size = struct.unpack("<HH", magic_and_size)

            assert magic == DATA_START_MAGIC, f"Magic mismatch, {magic=} {DATA_START_MAGIC=}"

            if size >= LARGE_DATA_MAGIC:
                large_size_data = await self.reader.read(4)

                size = struct.unpack("<I", large_size_data)

            data = ByteInterface(await self.reader.read(size + 1))

    async def dispatch_control(self):
        pass

    async def wait_for_control(self, name: str):
        pass
