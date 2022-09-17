from dataclasses import dataclass
from typing import TYPE_CHECKING, Self


if TYPE_CHECKING:
    from wizmsg import ByteInterface


@dataclass
class Control:
    opcode: int

    @classmethod
    def from_data(cls, data: "ByteInterface") -> Self:
        raise NotImplementedError()

    def to_data(self) -> bytes:
        raise NotImplementedError()


@dataclass
class SessionOffer(Control):
    session_id: int

    opcode: int = 0

    @classmethod
    def from_data(cls, data: "ByteInterface") -> Self:
        session_id = data.unsigned2()

        # TODO: timestamp

        return cls(session_id=session_id)

    def to_data(self) -> bytes:
        pass


@dataclass
class ServerKeepAlive(Control):
    session_id: int
