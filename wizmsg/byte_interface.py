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

    # def write_format_string(self, format_string: str, data: UnpackedData):
    #     packed = struct.pack(format_string, data)
    #     self.write(packed)

    def bool(self) -> bool:
        return self.read_format_string("?")

    def float(self) -> float:
        return self.read_format_string("<f")

    def double(self) -> float:
        return self.read_format_string("<d")

    def unsigned1(self) -> int:
        return self.read_format_string("<B")

    def signed1(self) -> int:
        return self.read_format_string("<b")

    def unsigned2(self) -> int:
        return self.read_format_string("<H")

    def signed2(self) -> int:
        return self.read_format_string("<h")

    def unsigned4(self) -> int:
        return self.read_format_string("<I")

    def signed4(self) -> int:
        return self.read_format_string("<i")

    def unsigned8(self) -> int:
        return self.read_format_string("<Q")

    def signed8(self) -> int:
        return self.read_format_string("<q")
