from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from wizmsg import ByteInterface


@dataclass
class Control:
    opcode: int

    # TODO: 3.11 replace this with typing.Self
    @classmethod
    def from_data(cls, data: "ByteInterface") -> "Control":
        raise NotImplementedError()

    def to_data(self) -> bytes:
        raise NotImplementedError()


@dataclass
class SessionOffer(Control):
    session_id: int
    timestamp: int
    milliseconds: int

    crypto_flags: int
    crypto_key_slot: int
    crypto_key_mask: int
    crypto_challenge: bytes
    crypto_nonce: int
    crypto_signature: bytes

    opcode = 0

    @classmethod
    def from_data(cls, data: "ByteInterface") -> "SessionOffer":
        session_id = data.unsigned2()

        # TODO: 2038 max 4 byte timestamp reached
        # high 4 bytes
        data.unsigned4()

        timestamp = data.unsigned4()
        milliseconds = data.unsigned4()
        # crypto len
        data.unsigned4()

        crypto_flags = data.unsigned1()
        crypto_key_slot = data.unsigned1()
        crypto_key_mask = data.unsigned1()
        crypto_challenge_len = data.unsigned1()
        crypto_challenge = data.read(crypto_challenge_len)
        crypto_nonce = data.unsigned4()
        crypto_signature = data.read(256)

        # TODO: does this really exist
        # reserved
        data.unsigned1()

        return cls(
            session_id=session_id,
            timestamp=timestamp,
            milliseconds=milliseconds,
            crypto_flags=crypto_flags,
            crypto_key_slot=crypto_key_slot,
            crypto_key_mask=crypto_key_mask,
            crypto_challenge=crypto_challenge,
            crypto_nonce=crypto_nonce,
            crypto_signature=crypto_signature,
            # for some reason the default stuff doesn't work here
            opcode=0,
        )

    def to_data(self) -> bytes:
        raise NotImplementedError()


@dataclass
class KeepAlive(Control):
    session_id: int
    milliseconds: int
    session_minutes: int

    opcode = 3

    @classmethod
    def from_data(cls, data: "ByteInterface") -> "KeepAlive":
        session_id = data.unsigned2()
        milliseconds = data.unsigned2()
        session_minutes = data.unsigned2()

        return cls(
            session_id=session_id,
            milliseconds=milliseconds,
            session_minutes=session_minutes,
            opcode=3,
        )

    def to_data(self) -> bytes:
        raise NotImplementedError()


@dataclass
class KeepAliveResponse(KeepAlive):
    opcode = 4

    def to_data(self) -> bytes:
        raise NotImplementedError()


@dataclass
class SessionAccept(Control):
    unknown: int
    fnv: int
    challenge_answer: int
    echo: int
    timestamp: int
    key: bytes
    nonce: bytes

    opcode = 5

    @classmethod
    def from_data(cls, data: "ByteInterface") -> "SessionAccept":
        unknown = data.unsigned1()
        fnv = data.unsigned4()
        challenge_answer = data.unsigned4()
        echo = data.unsigned4()
        timestamp = data.signed4()
        key = data.read(16)
        nonce = data.read(16)

        return cls(
            unknown=unknown,
            fnv=fnv,
            challenge_answer=challenge_answer,
            echo=echo,
            timestamp=timestamp,
            key=key,
            nonce=nonce,
        )

    def to_data(self) -> bytes:
        raise NotImplementedError()
