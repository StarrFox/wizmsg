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

    def to_data(self, buffer: "ByteInterface") -> int:
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
        data.signed4()
        timestamp = data.signed4()
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

    def to_data(self, buffer: "ByteInterface") -> int:
        written = 0

        written += buffer.write_unsigned2(self.session_id)

        # TODO: 2038 max 4 byte timestamp reached
        written += buffer.write_signed4(0)
        written += buffer.write_signed4(self.timestamp)
        written += buffer.write_unsigned4(self.milliseconds)

        crypto_payload_pos = buffer.tell()
        written += buffer.write_unsigned4(0)

        written += buffer.write_unsigned1(self.crypto_flags)
        written += buffer.write_unsigned1(self.crypto_key_slot)
        written += buffer.write_unsigned1(self.crypto_key_mask)
        written += buffer.write_unsigned1(len(self.crypto_challenge))
        written += buffer.write(self.crypto_challenge)
        written += buffer.write_unsigned4(self.crypto_nonce)
        written += buffer.write(self.crypto_signature)

        current_pos = buffer.tell()
        buffer.seek(crypto_payload_pos)

        crypto_payload_len = current_pos - crypto_payload_pos + 4
        buffer.write_unsigned4(crypto_payload_len)

        buffer.seek(current_pos)

        written += buffer.write_unsigned1(0)

        return written


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

    def to_data(self, buffer: "ByteInterface") -> int:
        written = 0

        written += buffer.write_unsigned2(self.session_id)
        written += buffer.write_unsigned2(self.milliseconds)
        written += buffer.write_unsigned2(self.session_minutes)

        return written


@dataclass
class KeepAliveResponse(KeepAlive):
    opcode = 4


@dataclass
class SessionAccept(Control):
    timestamp: int
    milliseconds: int
    session_id: int

    unknown: int
    fnv: int
    challenge_answer: int
    echo: int
    timestamp2: int
    key: bytes
    nonce: bytes

    opcode = 5

    @classmethod
    def from_data(cls, data: "ByteInterface") -> "SessionAccept":
        data.unsigned2()

        # TODO: 2038 max 4 byte timestamp reached
        data.signed4()
        timestamp = data.signed4()
        milliseconds = data.unsigned4()

        session_id = data.unsigned2()

        # crypto len
        data.unsigned4()

        unknown = data.unsigned1()
        fnv = data.unsigned4()
        challenge_answer = data.unsigned4()
        echo = data.unsigned4()
        timestamp2 = data.signed4()
        key = data.read(16)
        nonce = data.read(16)

        data.unsigned1()

        return cls(
            timestamp=timestamp,
            milliseconds=milliseconds,
            session_id=session_id,
            unknown=unknown,
            fnv=fnv,
            challenge_answer=challenge_answer,
            echo=echo,
            timestamp2=timestamp2,
            key=key,
            nonce=nonce,
            opcode=5,
        )

    def to_data(self, buffer: "ByteInterface") -> int:
        written = 0

        written += buffer.write_unsigned2(0)

        # TODO: 2038 max 4 byte timestamp reached
        written += buffer.write_signed4(0)
        written += buffer.write_signed4(self.timestamp)
        written += buffer.write_unsigned4(self.milliseconds)

        written += buffer.write_unsigned2(self.session_id)

        crypto_payload_pos = buffer.tell()
        buffer.write_unsigned4(0)

        written += buffer.write_unsigned1(self.unknown)
        written += buffer.write_unsigned4(self.fnv)
        written += buffer.write_unsigned4(self.challenge_answer)
        written += buffer.write_unsigned4(self.echo)
        written += buffer.write_signed4(self.timestamp2)
        written += buffer.write(self.key)
        written += buffer.write(self.nonce)

        current_pos = buffer.tell()
        buffer.seek(crypto_payload_pos)

        crypto_payload_len = current_pos - crypto_payload_pos + 4
        buffer.write_unsigned4(crypto_payload_len)

        buffer.seek(current_pos)

        written += buffer.write_unsigned1(0)

        return written
