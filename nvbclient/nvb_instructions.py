from collections import defaultdict

from .constants import MSG_PREFIX


OP_NULL = b'\x00'
OP_CREATE = b'\x01'


class Instruction:
    PREFIX = MSG_PREFIX
    def __init__(self):
        self.op_code = OP_NULL

    def _encode__with_extra_bytes(self, *bs):
        return self.PREFIX + self.op_code + b''.join(bs)





class InitNetwork(Instruction):

    def __init__(self, name: bytes):
        super().__init__()
        self.name = name
        self.op_code = OP_CREATE

        assert len(self.name) < 20

    def as_bytes(self):
        return self._encode_with_extra_bytes(self.name)
