from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from wizmsg import ProtocolDefinition, MessageDefinition


class Message:
    def __init__(self, definition: "MessageDefinition"):
        self.definition = definition

    @classmethod
    async def from_data(cls):
        """Only gets the arg data"""
        pass

    async def to_data(self) -> bytes:
        """Only returns the arg data"""
        pass


class Protocol:
    def __init__(self, definition: "ProtocolDefinition"):
        self.definition = definition

    # todo: better name for data -> Message
    async def process_message(self) -> Message:
        """Gets data after service id"""
        pass

    async def prepare_message(self, message: Message) -> bytes:
        """Returns data after service id (service id not included?)"""
        pass
