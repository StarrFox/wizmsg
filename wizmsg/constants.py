DATA_START_MAGIC = 0xF00D
LARGE_DATA_MAGIC = 0x8000

WIZ_TYPE_CONVERSION_TABLE = {
    "BYT": "signed1",
    "UBYT": "unsigned1",
    "SHRT": "signed2",
    "USHRT": "unsigned2",
    "INT": "signed4",
    "UINT": "unsigned4",
    # note: this is 100% 8 bytes, stop changing it to 4
    "GID": "unsigned8",
    "STR": "string",
    "WSTR": "wide_string",
    "FLT": "float",
}