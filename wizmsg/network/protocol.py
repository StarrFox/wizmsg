from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger

from wizmsg import WIZ_TYPE_CONVERSION_TABLE

if TYPE_CHECKING:
    from wizmsg import ByteInterface, MessageDefinition, ProtocolDefinition


@dataclass
class MessageData:
    service_id: int
    order_id: int

    name: str
    # param name: value
    parameters: dict[str, Any]


class Message:
    def __init__(self, definition: "MessageDefinition"):
        self.definition = definition

    def process_message_data(
        self, service_id: int, data: "ByteInterface"
    ) -> MessageData:
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
            else:
                value = getattr(data, read_method)()

            logger.debug(
                f"{name=} {value=} {param_type=} rest={data.getbuffer()[data.tell():].hex(' ')}"
            )

            parameters[name] = value

        return MessageData(
            service_id, self.definition.order, self.definition.name, parameters
        )

    def prepare_message_data(
        self, data: "ByteInterface", message_data: MessageData
    ) -> int:
        written = 0

        for name, value in message_data.parameters.items():
            parameter_definition = self.definition.parameters[name]
            write_method = (
                "write_" + WIZ_TYPE_CONVERSION_TABLE[parameter_definition.type]
            )

            if write_method == "write_string" and isinstance(value, str):
                value = value.encode()

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

        message_data = message.process_message_data(self.definition.service_id, data)

        # there should be a single null byte left in the buffer at this point
        data.seek(1)

        return message_data

    def prepare_protocol_data(
        self, buffer: "ByteInterface", message_data: MessageData
    ) -> int:
        written = 0

        service_id = message_data.service_id
        order_id = message_data.order_id

        message = self.messages.get(order_id)
        if message is None:
            raise RuntimeError(f"Got invalid message order {order_id}")

        written += buffer.write_unsigned1(service_id)
        written += buffer.write_unsigned1(order_id)

        dml_length_pos = buffer.tell()
        written += buffer.write_unsigned2(0)

        message_bytes = message.prepare_message_data(buffer, message_data)

        current_pos = buffer.tell()
        buffer.seek(dml_length_pos)
        buffer.write_unsigned2(message_bytes)
        buffer.seek(current_pos)

        # trailing null byte
        written += buffer.write_unsigned1(0)

        return written + message_bytes

    # TODO: what was this supposed to do
    # def prepare_message(self, message: Message) -> bytes:
    #     """Returns data after service id (service id not included?)"""
    #     pass
