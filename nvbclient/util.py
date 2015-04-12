from .constants import ENDIAN

def convert_se_bytes(se_bytes: bytes):
    return int.from_bytes(se_bytes, ENDIAN)