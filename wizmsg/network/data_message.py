from dataclasses import dataclass

from wizmsg import ByteInterface


# see: https://kronos-project.github.io/grimoire/internals/protocol/index.html
@dataclass
class DataMessage:
    raw_data: ByteInterface

    @classmethod
    def from_data(cls, data: ByteInterface):
        """
        Network message from bytes
        """
        pass

    def to_data(self) -> bytes:
        pass
