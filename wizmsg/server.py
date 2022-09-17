import asyncio
import struct


from wizmsg import DATA_START_MAGIC, LARGE_DATA_MAGIC, network
from .byte_interface import ByteInterface


class Server:
    def __init__(self, address: str, port: int = 8000):
        self.address = address
        self.port = port

        self.server = None
        self.message_processor = network.Processor()
        self.sessions = []

    async def _client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # TODO: figure out a nice way to not duplicate this code
        magic_and_size = await reader.read(4)

        magic, size = struct.unpack("<HH", magic_and_size)

        assert magic == DATA_START_MAGIC, f"Magic mismatch, {magic=} {DATA_START_MAGIC=}"

        if size >= LARGE_DATA_MAGIC:
            large_size_data = await reader.read(4)

            size = struct.unpack("<I", large_size_data)

        data = ByteInterface(await reader.read(size + 1))
        message = self.message_processor.process_message_data(data)

    async def run(self):
        self.server = await asyncio.start_server(
            self._client_connection,
            host=self.address,
            port=self.port,
        )

        async with self.server:
            await self.server.serve_forever()
