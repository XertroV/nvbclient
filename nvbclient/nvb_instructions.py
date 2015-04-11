from collections import defaultdict

from .constants import MSG_PREFIX

class Instruction:
    PREFIX = MSG_PREFIX
    def __init__(self):
        None

    @staticmethod
    def _encode_bytes(*bs):
        return Instruction.PREFIX + b''





class InitNetwork(Instruction):

    def __init__(self, name: bytes):
        super().__init__()
        self.name = name
        assert len(self.name) < 20

    def as_bytes(self):
        return self._encode_bytes()
