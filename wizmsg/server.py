import asyncio
from pathlib import Path

from .concepts import Protocol


class Server:
    def __init__(self, address: str, port: int = 8000):
        self.address = address
        self.port = port

        self.protocols = []
        self.server = None

    def load_protocol(self, protocol_path: str | Path) -> Protocol:
        if isinstance(protocol_path, str):
            protocol_path = Path(protocol_path)

        protocol = Protocol.from_xml_file(protocol_path)

        self.protocols.append(protocol)

        return protocol

    def _register_protocol(self, protocol: Protocol):
        """
        {message_name: {param_name: type (int)}}
        """
        pass

    async def _client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(100)

        print(f"{data=}")

    async def start(self):
        self.server = await asyncio.start_server(
            self._client_connection,
            host=self.address,
            port=self.port,
        )

        async with self.server:
            await self.server.serve_forever()

    def run(self):
        asyncio.run(self.start())
