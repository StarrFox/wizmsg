import asyncio
import struct
from pathlib import Path
from io import StringIO

from wizmsg import DATA_START_MAGIC, LARGE_DATA_MAGIC
from .protocol import Protocol
from .byte_interface import ByteInterface


class Server:
    def __init__(self, address: str, port: int = 8000):
        self.address = address
        self.port = port

        # protocol id: Protocol
        self.protocols: dict[int, Protocol] = {}
        self.server = None

        self.sessions = []

    def load_protocol(self, protocol_path: str | Path | StringIO) -> Protocol:
        if isinstance(protocol_path, str):
            protocol_path = Path(protocol_path)

        protocol = Protocol.from_xml_file(protocol_path)

        self._register_protocol(protocol)

        return protocol

    # this is because we already accept strings as paths
    def load_protocol_from_string(self, protocol_string: str | StringIO) -> Protocol:
        if isinstance(protocol_string, str):
            protocol_string = StringIO(protocol_string)

        return self.load_protocol(protocol_string)

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
        magic_and_size = await reader.read(4)

        magic, size = struct.unpack("<HH", magic_and_size)

        assert magic == DATA_START_MAGIC, f"Magic mismatch, {magic=} {DATA_START_MAGIC=}"

        if size >= LARGE_DATA_MAGIC:
            large_size_data = await reader.read(4)

            size = struct.unpack("<I", large_size_data)

        data = ByteInterface(await reader.read(size))

    async def run(self):
        self.server = await asyncio.start_server(
            self._client_connection,
            host=self.address,
            port=self.port,
        )

        async with self.server:
            await self.server.serve_forever()
