from collections import defaultdict

from .constants import MSG_PREFIX, ENDIAN


OP_NULL = b'\x00'
OP_CREATE = b'\x01'


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

    def __init__(self, name):
        super().__init__()
        self.op_code = OP_CREATE
        self.name = bytes(name.encode() if type(name) is str else name)
        self._extra_bytes = len(self.name).to_bytes(1, ENDIAN) + self.name

        assert len(self.name) < 20


instruction_map = {
    'new': NewNetwork,
}
def instruction_lookup(i):
    return instruction_map.get(i)