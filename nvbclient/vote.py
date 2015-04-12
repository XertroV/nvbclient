
from .constants import MSG_PREFIX

class Vote:
    """ Main class handling forming valid messages for the network.
    """
    PREFIX = MSG_PREFIX

    def __init__(self, vote_type, ):
        self._bytes = bytes(MSG_PREFIX)
        self._bytes += {
            'new': b'\x00'
        }.get(vote_type)

    @classmethod
    def from_json(cls, d):
        Vote(**d)

    def to_bytes(self):
        return self._bytes