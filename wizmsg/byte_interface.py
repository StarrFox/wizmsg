import struct
import typing
from io import BytesIO


UnpackedData: typing.TypeAlias = typing.Any | tuple[typing.Any]


class ByteInterface(BytesIO):
    def read_format_string(self, format_string: str) -> UnpackedData:
        size = struct.calcsize(format_string)
        data = self.read(size)
        unpacked = struct.unpack(format_string, data)

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked

    def write_format_string(self, format_string: str, data: UnpackedData) -> int:
        """
        returns the number of bytes written
        """
        packed = struct.pack(format_string, data)
        return self.write(packed)

    def string(self) -> str:
        # 2 bytes for length
        length = self.unsigned2()
        data = self.read(length)
        return data.decode()

    def write_string(self, string: str):
        length = len(string)
        self.write_unsigned2(length)
        self.write(string.encode())

    def wide_string(self) -> str:
        # length is number of characters
        length = self.unsigned2() * 2
        data = self.read(length)
        return data.decode("utf-16")

    def write_wide_string(self, wide_string: str):
        length = len(wide_string)
        self.write_unsigned2(length)
        self.write(wide_string.encode("utf-16"))

    def bool(self) -> bool:
        return self.read_format_string("?")

    def write_bool(self, data: bool) -> int:
        return self.write_format_string("?", data)

    def float(self) -> float:
        return self.read_format_string("<f")

    def write_float(self, data: float) -> int:
        return self.write_format_string("<f", data)

    def double(self) -> float:
        return self.read_format_string("<d")

    def write_double(self, data: float) -> int:
        return self.write_format_string("<d", data)

    def unsigned1(self) -> int:
        return self.read_format_string("<B")

    def write_unsigned1(self, data: int) -> int:
        return self.write_format_string("<B", data)

    def signed1(self) -> int:
        return self.read_format_string("<b")

    def write_signed1(self, data: int) -> int:
        return self.write_format_string("<b", data)

    def unsigned2(self) -> int:
        return self.read_format_string("<H")

    def write_unsigned2(self, data: int) -> int:
        return self.write_format_string("<H", data)

    def signed2(self) -> int:
        return self.read_format_string("<h")

    def write_signed2(self, data: int) -> int:
        return self.write_format_string("<h", data)

    def unsigned4(self) -> int:
        return self.read_format_string("<I")

    def write_unsigned4(self, data: int) -> int:
        return self.write_format_string("<I", data)

    def signed4(self) -> int:
        return self.read_format_string("<i")

    def write_signed4(self, data: int) -> int:
        return self.write_format_string("<i", data)

    def unsigned8(self) -> int:
        return self.read_format_string("<Q")

    def write_unsigned8(self, data: int) -> int:
        return self.write_format_string("<Q", data)

    def signed8(self) -> int:
        return self.read_format_string("<q")

    def write_signed8(self, data: int) -> int:
        return self.write_format_string("<q", data)
