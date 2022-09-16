from .byte_interface import ByteInterface
from .protocol_definition import ProtocolDefinition, MessageDefinition, MessageDefinitionParameter
from .server import Server

DATA_START_MAGIC = 0xF00D
LARGE_DATA_MAGIC = 0x8000

WIZ_TYPE_CONVERSION_TABLE = {
    "BYT": "signed1",
    "UBYT": "unsigned1",
    "INT": "signed4",
    "UINT": "unsigned4",
    "GID": "unsigned8",
    "STR": "string",
    "WSTR": "wide_string",
    "FLT": "float",
}
