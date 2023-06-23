import struct
import typing
from io import BytesIO

UnpackedData: typing.TypeAlias = typing.Any | tuple[typing.Any]


class ByteInterface(BytesIO):
    def read_format_string(self, format_string: str) -> UnpackedData:
        size = struct.calcsize(format_string)
        unpacked = struct.unpack(format_string, self.read(size))

        if len(unpacked) == 1:
            return unpacked[0]

        return unpacked

    def _read_single(self, format_string: str) -> typing.Any:
        result = self.read_format_string(format_string)
        assert not isinstance(result, tuple)
        return result

    def write_format_string(self, format_string: str, data: UnpackedData) -> int:
        """
        returns the number of bytes written
        """
        packed = struct.pack(format_string, data)
        return self.write(packed)

    def string(self) -> bytes:
        length = self.unsigned2()
        return self.read(length)

    def write_string(self, string: bytes):
        self.write_unsigned2(len(string))
        self.write(string)

    def wide_string(self) -> str:
        length = self.unsigned2() * 2
        return self.read(length).decode("utf-16-le")

    def write_wide_string(self, wide_string: str):
        wide_string_encoded = wide_string.encode("utf-16-le")
        self.write_unsigned2(len(wide_string_encoded))
        self.write(wide_string_encoded)

    def bool(self) -> bool:
        return self._read_single("?")

    def write_bool(self, data: "bool") -> int:
        return self.write_format_string("?", data)

    def float(self) -> float:
        return self._read_single("<f")

    def write_float(self, data: "float") -> int:
        return self.write_format_string("<f", data)

    def double(self) -> "float":
        return self._read_single("<d")

    def write_double(self, data: "float") -> int:
        return self.write_format_string("<d", data)

    def unsigned1(self) -> int:
        return self._read_single("<B")

    def write_unsigned1(self, data: int) -> int:
        return self.write_format_string("<B", data)

    def signed1(self) -> int:
        return self._read_single("<b")

    def write_signed1(self, data: int) -> int:
        return self.write_format_string("<b", data)

    def unsigned2(self) -> int:
        return self._read_single("<H")

    def write_unsigned2(self, data: int) -> int:
        return self.write_format_string("<H", data)

    def signed2(self) -> int:
        return self._read_single("<h")

    def write_signed2(self, data: int) -> int:
        return self.write_format_string("<h", data)

    def unsigned4(self) -> int:
        return self._read_single("<I")

    def write_unsigned4(self, data: int) -> int:
        return self.write_format_string("<I", data)

    def signed4(self) -> int:
        return self._read_single("<i")

    def write_signed4(self, data: int) -> int:
        return self.write_format_string("<i", data)

    def unsigned8(self) -> int:
        return self._read_single("<Q")

    def write_unsigned8(self, data: int) -> int:
        return self.write_format_string("<Q", data)

    def signed8(self) -> int:
        return self._read_single("<q")

    def write_signed8(self, data: int) -> int:
        return self.write_format_string("<q", data)
