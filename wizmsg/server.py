import asyncio
from pathlib import Path

from .protocol import Protocol


class Server:
    def __init__(self, address: str, port: int = 8000):
        self.address = address
        self.port = port

        # protocol id: Protocol
        self.protocols: dict[int, Protocol] = {}
        self.server = None

    def load_protocol(self, protocol_path: str | Path) -> Protocol:
        if isinstance(protocol_path, str):
            protocol_path = Path(protocol_path)

        protocol = Protocol.from_xml_file(protocol_path)

        self._register_protocol(protocol)

        return protocol

    def load_protocols_from_directory(
            self,
            protocol_directory: str | Path,
            *,
            allowed_glob: str = "*.xml",
    ) -> list[Protocol]:
        """
        server.load_protocols_from_directory("messages", allowed_glob="*Messages.xml")
        """
        if isinstance(protocol_directory, str):
            protocol_directory = Path(protocol_directory)

        protocols = []
        for protocol_file in protocol_directory.glob(allowed_glob):
            protocols.append(self.load_protocol(protocol_file))

        return protocols

    def _register_protocol(self, protocol: Protocol):
        """
        abstract protocol registering in the likely case that more logic needs to be added
        """
        if self.protocols.get(protocol.service_id):
            raise ValueError(f"Protocol id {protocol.service_id} is already registered")

        self.protocols[protocol.service_id] = protocol

    async def _client_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(100)

        print(f"{data=}")

    async def run(self):
        self.server = await asyncio.start_server(
            self._client_connection,
            host=self.address,
            port=self.port,
        )

        async with self.server:
            await self.server.serve_forever()
