from pycoin.key import Key

from .constants import ENDIAN

def bitcoin_key_from_bytes(key: bytes):
  return Key(secret_exponent=int.from_bytes(key, ENDIAN))
