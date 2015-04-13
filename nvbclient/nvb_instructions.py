from collections import defaultdict

from pycoin.key import Key

from .constants import MSG_PREFIX, ENDIAN


OP_NULL = b'\x00'
OP_CREATE = b'\x01'

OP_CAST = b'\x10'
OP_DELEGATE = b'\x11'


class Instruction:
    PREFIX = MSG_PREFIX
    def __init__(self):
        self.op_code = OP_NULL
        self._extra_bytes = b''

    def _encode_with_extra_bytes(self, *bs):
        return self.PREFIX + self.op_code + b''.join(bs)

    def to_bytes(self):
        return self.PREFIX + self.op_code + self._extra_bytes



class NewNetwork(Instruction):
    """PREFIX[3] OP_CREATE[1] name[<20]"""

    def __init__(self, name):
        super().__init__()
        self.op_code = OP_CREATE
        self.name = bytes(name.encode() if type(name) is str else name)
        self._extra_bytes = self.name

        assert len(self.name) < 20


class CastVote(Instruction):
    """PREFIX[3] OP_CAST[1] vote_number[1] resolution[<10]"""

    def __init__(self, vote_number, resolution):
        super().__init__()
        self.op_code = OP_CAST
        self.vote_number = int(vote_number).to_bytes(1, ENDIAN)
        self.resolution = bytes(resolution.upper().encode())
        self._extra_bytes = self.vote_number + self.resolution

        assert len(self.resolution) < 10


class DelegateVote(Instruction):
    """PREFIX[3] OP_DELEGATE[1] categories[1] address[20]
    numbers in [] indicate # bytes"""

    def __init__(self, address, categories):
        super().__init__()
        self.op_code = OP_DELEGATE
        self.hash160 = bytes(Key.from_text(address).hash160())
        self.categories = int(categories).to_bytes(1, ENDIAN)
        self._extra_bytes = self.categories + self.hash160

        assert len(self.hash160) == 20


instruction_map = {
    'new': NewNetwork,
    'cast': CastVote,
    'delegate': DelegateVote,
}
def instruction_lookup(i):
    return instruction_map.get(i)