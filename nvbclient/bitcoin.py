from pycoin.key import Key

from blockchain import blockexplorer, pushtx  # todo: add redundancy

from .constants import ENDIAN

def bitcoin_key_from_bytes(key: bytes):
    return Key(secret_exponent=int.from_bytes(key, ENDIAN))


def get_utxos_for_address(address):
    r = blockexplorer.get_unspent_outputs(address)
    assert type(r) == list
    return r


def pushtx(tx):
    return pushtx.pushtx(tx)