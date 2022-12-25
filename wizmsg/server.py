import asyncio

from wizmsg import network


class Server:
    def __init__(self, address: str, port: int = 8000):
        self.address = address
        self.port = port

        self.server = None
        self.message_processor = network.Processor()
        self.sessions = []

    async def _client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read()
        message = self.message_processor.process_frame(data)

    async def run(self):
        self.server = await asyncio.start_server(
            self._client_connection,
            host=self.address,
            port=self.port,
        )

        async with self.server:
            await self.server.serve_forever()
