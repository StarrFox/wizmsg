from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger

from wizmsg import WIZ_TYPE_CONVERSION_TABLE

if TYPE_CHECKING:
    from wizmsg import ByteInterface, MessageDefinition, ProtocolDefinition


@dataclass
class MessageData:
    name: str
    # param name: value
    parameters: dict[str, Any]


class Message:
    def __init__(self, definition: "MessageDefinition"):
        self.definition = definition

    def process_message_data(self, data: "ByteInterface") -> MessageData:
        """Only gets the arg data"""
        parameters = {}
        for parameter_definition in self.definition.parameters.values():
            name = parameter_definition.name
            param_type = parameter_definition.type
            read_method = WIZ_TYPE_CONVERSION_TABLE.get(param_type)

            if read_method is None:
                raise RuntimeError(f"Missing read method for type {param_type}")

            # TODO: wide_string
            if read_method == "string":
                value = getattr(data, read_method)()
                try:
                    value = value.decode()
                except UnicodeDecodeError:
                    # TODO: return this as byte or something
                    logger.warning(
                        "ignoring string decoding failure; likely class data"
                    )
                    value = value
            else:
                value = getattr(data, read_method)()

            logger.debug(
                f"{name=} {value=} {param_type=} rest={data.getbuffer()[data.tell():].hex(' ')}"
            )

            parameters[name] = value

        return MessageData(self.definition.name, parameters)

    def unprocess_message_data(self, data: "ByteInterface", message_data: MessageData) -> int:
        written = 0

        for name, value in message_data.parameters.items():
            parameter_definition = self.definition.parameters[name]
            write_method = "write_" + WIZ_TYPE_CONVERSION_TABLE[parameter_definition.type]

            # TODO: write_wide_string
            if write_method == "write_string":
                if isinstance(value, bytes):
                    written += data.write(value)
                    continue

                try:
                    written += getattr(data, write_method)(value.encode())
                except UnicodeEncodeError:
                    logger.warning(
                        "ignoring string encoding failure; likely class data"
                    )
            else:
                written += getattr(data, write_method)(value)

        return written


class Protocol:
    def __init__(self, definition: "ProtocolDefinition"):
        self.definition = definition

        messages = {}
        for order, message_definition in self.definition.messages.items():
            messages[order] = Message(message_definition)

        # order: Message
        self.messages: dict[int, Message] = messages

    def process_protocol_data(self, data: "ByteInterface") -> MessageData:
        """Gets data after service id"""
        order_id = data.unsigned1()
        length = data.unsigned2()
        message = self.messages.get(order_id)

        if message is None:
            raise RuntimeError(f"Got invalid message order {order_id}")

        logger.debug(
            f"{order_id=} {length=} {message.definition.name=} rest={data.getbuffer()[data.tell():].hex(' ')}"
        )

        message_data = message.process_message_data(data)

        # there should be a single null byte left in the buffer at this point
        data.seek(1)

        return message_data

    def prepare_protocol_data(self, buffer: "ByteInterface", order_id: int, message_data: MessageData) -> int:
        message = self.messages.get(order_id)

        if message is None:
            raise RuntimeError(f"Got invalid message order {order_id}")
        
        written = 0
        written += buffer.write_unsigned1(order_id)
        length_position = buffer.tell()

        written_message = message.unprocess_message_data(buffer, message_data)

        checkpoint = buffer.tell()
        buffer.seek(length_position)

        written += buffer.write_unsigned2(written_message)

        buffer.seek(checkpoint)

        # trailing null byte
        written += buffer.write_unsigned1(0)

        return written + written_message

    # TODO: what was this supposed to do
    # def prepare_message(self, message: Message) -> bytes:
    #     """Returns data after service id (service id not included?)"""
    #     pass
