DATA_START_MAGIC = 0xF00D
LARGE_DATA_MAGIC = 0x8000

from .byte_interface import ByteInterface
from .protocol import Protocol, Message, MessageParameter
from .server import Server
