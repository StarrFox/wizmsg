from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger

from wizmsg import WIZ_TYPE_CONVERSION_TABLE


if TYPE_CHECKING:
    from wizmsg import ProtocolDefinition, MessageDefinition, ByteInterface


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
        for parameter_definition in self.definition.parameters:
            name = parameter_definition.name
            param_type = parameter_definition.type

            read_method = WIZ_TYPE_CONVERSION_TABLE.get(param_type)

            if read_method is None:
                raise RuntimeError(f"Missing read method for type {param_type}")

            if read_method == "string":
                try:
                    value = getattr(data, read_method)()
                except UnicodeDecodeError:
                    # TODO: log a warning here or something
                    logger.warning("ignoring string decoding failure; likely class data")
                    value = None
            else:
                value = getattr(data, read_method)()

            logger.debug(f"{name=} {value=} {param_type=} rest={data.getbuffer()[data.tell():].hex(' ')}")

            parameters[name] = value

        return MessageData(self.definition.name, parameters)


class Protocol:
    def __init__(self, definition: "ProtocolDefinition"):
        self.definition = definition

        messages = {}
        for order, message_definition in self.definition.messages.items():
            messages[order] = Message(message_definition)

        # order: Message
        self.messages = messages

    def process_protocol_data(self, data: "ByteInterface") -> MessageData:
        """Gets data after service id"""
        order_id = data.unsigned1()

        length = data.unsigned2()

        message = self.messages.get(order_id)

        if message is None:
            raise RuntimeError(f"Got invalid message order {order_id}")

        logger.debug(f"{order_id=} {length=} {message.definition.name=} rest={data.getbuffer()[data.tell():].hex(' ')}")

        message_data = message.process_message_data(data)
        # there should be a single null byte left in the buffer at this point

        return message_data

    # def prepare_message(self, message: Message) -> bytes:
    #     """Returns data after service id (service id not included?)"""
    #     pass
