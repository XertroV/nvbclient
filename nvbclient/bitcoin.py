from pycoin.key import Key

from blockchain import blockexplorer, pushtx  # todo: add redundancy

from binascii import unhexlify

from .constants import ENDIAN

def bitcoin_key_from_bytes(key: bytes):
    return Key(secret_exponent=int.from_bytes(key, ENDIAN))


def get_utxos_for_address(address):
    r = blockexplorer.get_unspent_outputs(address)
    assert type(r) == list
    return r


def update_utxos():
    address = DBSession.query(KeyStore).filter(KeyStore.name == 'primary').first().address
    for output in blockexplorer.get_unspent_outputs(address):
        d = dict(output.__dict__)
        d['tx_hash'] = unhexlify(d['tx_hash'])
        d['script'] = unhexlify(d['script'])
        d['address'] = address
        del(d['tx_index'], d['value_hex'])
        if 0 == len(DBSession.query(UTXOs).filter(UTXOs.tx_hash == d['tx_hash'], UTXOs.tx_output_n == d['tx_output_n']).all()):
            DBSession.add(UTXOs(**d))


def pushtx(tx):
    """tx should be hex encoded"""
    return pushtx.pushtx(tx)