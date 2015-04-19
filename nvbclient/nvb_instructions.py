from collections import defaultdict

from pycoin.key import Key

from .constants import MSG_PREFIX, ENDIAN


OP_NULL = b'\x00'
OP_CREATE = b'\x01'
OP_MOD_RES = b'\x02'
OP_EMPOWER = b'\x03'

OP_CAST = b'\x10'
OP_DELEGATE = b'\x11'


def validate_resolution(r):
    assert type(r) == bytes
    assert len(r) < 15

def validate_url(u):
    assert type(u) == bytes
    assert len(u) < 15

def validate_hash160(h):
    assert type(h) == bytes
    assert len(h) == 20

def validate_comment(c):
    assert type(c) == bytes
    assert len(c) <= 40


def len_to_one_byte(i):
    return len(i).to_bytes(1, ENDIAN)

class Instruction:
    PREFIX = MSG_PREFIX
    def __init__(self):
        self.op_code = OP_NULL
        self._extra_bytes = b''

    def _encode_with_extra_bytes(self, *bs):
        return self.PREFIX + self.op_code + b''.join(bs)

    def to_bytes(self):
        return self.PREFIX + self.op_code + self._extra_bytes


# TODO: port references over to nvb_lib


class CreateNetwork(Instruction):
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

        validate_resolution(self.resolution)


class ModResolution(Instruction):
    """PREFIX[3] OP_MOD_RES[1] categories[1] end_timestamp[4] res_len[1] resolution[<15] url_len[1] url[<15]"""

    def __init__(self, categories, end_timestamp, resolution, url):
        super().__init__()
        self.op_code = OP_MOD_RES
        self.categories = int(categories).to_bytes(1, ENDIAN)
        self.end_timestamp = int(end_timestamp).to_bytes(4, ENDIAN)
        self.resolution = bytes(resolution.encode())
        self.url = bytes(url.encode())

        self._extra_bytes = self.categories + self.end_timestamp + \
            len_to_one_byte(self.resolution) + self.resolution + \
            len_to_one_byte(self.url) + self.url

        validate_url(self.url)
        validate_resolution(self.resolution)


class DelegateVote(Instruction):
    """PREFIX[3] OP_DELEGATE[1] categories[1] address[20]
    numbers in [] indicate # bytes"""

    def __init__(self, address, categories):
        super().__init__()
        self.op_code = OP_DELEGATE
        self.hash160 = bytes(Key.from_text(address).hash160())
        self.categories = int(categories).to_bytes(1, ENDIAN)
        self._extra_bytes = self.categories + self.hash160

        validate_hash160(self.hash160)


class EmpowerVote(Instruction):
    """ PREFIX[3] OP_EMPOWER[1] votes[4] hash160[20]
    """

    def __init__(self, votes, address):
        super().__init__()
        self.op_code = OP_EMPOWER
        self.hash160 = bytes(Key.from_text(address).hash160())
        self.votes = int(votes).to_bytes(4, ENDIAN)
        self._extra_bytes = self.votes + self.hash160

        validate_hash160(self.hash160)


class CommentNulldata(Instruction):
    PREFIX = b''

    def __init__(self, comment):
        self.op_code = b''
        self.comment = comment.encode()
        self._extra_bytes = self.comment

        validate_comment(self.comment)


instruction_map = {
    'create': CreateNetwork,
    'cast': CastVote,
    'delegate': DelegateVote,
    'mod_res': ModResolution,
    'empower': EmpowerVote,
    'comment': CommentNulldata,
}
def instruction_lookup(i):
    return instruction_map.get(i)