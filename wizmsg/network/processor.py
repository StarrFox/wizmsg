from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from wizmsg import ByteInterface, ProtocolDefinition
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

    def process_message_data(self, data: ByteInterface | bytes, *, session: "Session" = None):
        """
        Gets data after data length
        """
        if isinstance(data, bytes):
            data = ByteInterface(data)

        is_control = data.bool()
        control_opcode = data.unsigned1()

        reserved = data.unsigned2()

        if is_control:
            raise NotImplementedError("forgot controls")

        else:
            service_id = data.unsigned1()

            protocol = self.protocols.get(service_id)

            if protocol is None:
                raise RuntimeError(f"Unexpected service id {service_id}")

            logger.debug(f"{control_opcode=} {reserved=} rest={data.getbuffer()[data.tell():].hex(' ')}")
            return protocol.process_protocol_data(data)


if __name__ == "__main__":
    test_data = bytes.fromhex("00 00 00 00 05 49 17 00 01 00 00 00 f2 68 2d 09 00 00 fc 01 05 00 4d 6f 75 6e 74 00")

    processor = Processor()
    processor.load_protocol("/home/starr/PycharmProjects/wizmsg/message_files/GameMessages.xml")

    message = processor.process_message_data(test_data)
    print(f"{message.name}: {message.parameters}")
