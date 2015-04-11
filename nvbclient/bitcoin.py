from pycoin.key import Key

from blockchain import blockexplorer

from binascii import unhexlify

from .constants import ENDIAN

from .models import (
    DBSession,
    UTXOs,
    KeyStore,
    )


def bitcoin_key_from_bytes(key: bytes):
    return Key(secret_exponent=int.from_bytes(key, ENDIAN))


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

