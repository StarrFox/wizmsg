from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from wizmsg import DATA_START_MAGIC, LARGE_DATA_MAGIC, ByteInterface, ProtocolDefinition
from wizmsg.network.controls import (
    KeepAlive,
    KeepAliveResponse,
    SessionAccept,
    SessionOffer,
)
from wizmsg.network.protocol import Protocol

if TYPE_CHECKING:
    from wizmsg import Session


class Processor:
    def __init__(self):
        # service id: definition
        self.protocols: dict[int, Protocol] = {}

    def load_protocol(self, protocol_path: str | Path | StringIO) -> Protocol:
        if isinstance(protocol_path, str):
            protocol_path = Path(protocol_path)

        protocol_definition = ProtocolDefinition.from_xml_file(protocol_path)
        protocol = Protocol(protocol_definition)

        self.protocols[protocol_definition.service_id] = protocol

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

    def process_message_data(
        self, data: ByteInterface, *, session: "Session" | None = None
    ):
        """
        Processes a data message
        """
        service_id = data.unsigned1()

        protocol = self.protocols.get(service_id)

        if protocol is None:
            raise RuntimeError(f"Unexpected service id {service_id}")

        return protocol.process_protocol_data(data)

    def process_control_data(self, data: ByteInterface, opcode: int):
        """
        Processes a control message
        """

        for control_type in (SessionOffer, SessionAccept, KeepAlive, KeepAliveResponse):
            if control_type.opcode == opcode:
                return control_type.from_data(data)

        raise ValueError(f"{opcode} is not a registered opcode")

    def process_frame(self, raw: bytes):
        raw_interface = ByteInterface(raw)

        magic = raw_interface.unsigned2()

        if magic != DATA_START_MAGIC:
            raise ValueError(
                f"Magic mismatch, expected: {DATA_START_MAGIC} got: {magic}"
            )

        # I don't really need size or large size
        size = raw_interface.unsigned2()

        if size >= LARGE_DATA_MAGIC:
            large_size_data = raw_interface.unsigned4()

        is_control = raw_interface.bool()
        control_opcode = raw_interface.unsigned1()

        reserved = raw_interface.unsigned2()

        if is_control:
            return self.process_control_data(raw_interface, control_opcode)

        else:
            return self.process_message_data(raw_interface)


if __name__ == "__main__":
    test_data = bytes.fromhex("0d f0 00 00 01 03 00 00 01 00 02 00 03 00")

    processor = Processor()

    message = processor.process_frame(test_data)
    print(f"{message}")
