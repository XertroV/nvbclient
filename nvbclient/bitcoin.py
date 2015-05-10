import random
import socket
import json
from time import time

from pycoin.key import Key
from pycoin.tx.tx_utils import create_tx, sign_tx
from pycoin.services.blockchain_info import spendables_for_address, send_tx
from pycoin.tx.TxOut import TxOut
from pycoin.tx.Tx import Tx
from pycoin.tx.pay_to.ScriptNulldata import ScriptNulldata

from blockchain import blockexplorer  # todo: add redundancy
from blockchain.exceptions import APIException

from binascii import unhexlify

from .constants import ENDIAN, PRIMARY, ELECTRUM_SERVERS, DUST, MIN_FEE
from .models import DBSession, KeyStore, UTXOs
from .auth import get_private_key


def bitcoin_key_from_bytes(key: bytes, testnet=False):
    return Key(secret_exponent=int.from_bytes(key, ENDIAN), testnet=testnet)


def get_address_for_key(name=PRIMARY):
    return DBSession.query(KeyStore).filter(KeyStore.name == name).first().address


def addr_to_testnet(addr):
    return Key(hash160=Key.from_text(addr).hash160(), netcode='XTN').address()


def get_utxos_for_address(address, testnet=False):
    if testnet:
        r = []
    else:
        r = blockexplorer.get_unspent_outputs(address)
    assert type(r) == list
    return r


def update_utxos():
    address = DBSession.query(KeyStore).filter(KeyStore.name == PRIMARY).first().address
    DBSession.query(UTXOs).delete()
    try:
        outputs = blockexplorer.get_unspent_outputs(address)
    except APIException as e:
        outputs = []
    for output in outputs:
        d = dict(output.__dict__)
        d['tx_hash'] = unhexlify(d['tx_hash'])
        d['script'] = unhexlify(d['script'])
        d['address'] = address
        del(d['tx_index'], d['value_hex'])
        if 0 == len(DBSession.query(UTXOs).filter(UTXOs.tx_hash == d['tx_hash'], UTXOs.tx_output_n == d['tx_output_n']).all()):
            DBSession.add(UTXOs(**d))
    return len(outputs)


def total_balance():
    utxos = DBSession.query(UTXOs).all()
    balance = sum(map(lambda u : u.value, utxos))
    return balance


def trim_spendables(spendables):
    last_trimmed = None
    # cut many spendables + one extra off so we can add it back at the end
    while len(spendables) >= 1 and sum((s.coin_value for s in spendables)) + MIN_FEE > DUST*2:
        last_trimmed = random.choice([(s.coin_value, s) for s in spendables])[1]
        spendables.remove(last_trimmed)
    spendables.append(last_trimmed)
    return spendables


def create_stock_tx(user=PRIMARY, use_smallest_spendables=True, extra_payables=[]):
    address = get_address_for_key(user)
    spendables = spendables_for_address(address)
    if use_smallest_spendables:
        spendables = trim_spendables(spendables)
    tx = create_tx(spendables, [address] + extra_payables, fee=10000)
    return tx

def mix_nulldata_into_tx(nulldata, tx):
    tx.txs_out.insert(0, TxOut(0, ScriptNulldata(nulldata).script()))
    return tx


def make_signed_tx_from_vote(vote, password, user=PRIMARY, extra_payables=[]):
    key = get_private_key(password, user)
    if key is None:
        raise Exception('Password Incorrect')
    tx = mix_nulldata_into_tx(vote.to_bytes(), create_stock_tx(user, extra_payables=extra_payables))
    sign_tx(tx, [key.wif()])
    return tx


def sendtx(hex_tx, testnet=False):
    # TODO : TEST! Currently untested. Copypasted from opreturn.ninja
    if testnet:
        raise NotImplementedError()
    try:
        server = random.choice(list(ELECTRUM_SERVERS.items()))
        s = socket.create_connection(server)
        s.send(json.dumps({"id": "nvbclient-{}".format(time()), "method": "blockchain.transaction.broadcast", "params": [hex_tx]}).encode() + b'\n')
        electrum_response = json.loads(s.recv(2048)[:-1].decode())  # the slice is to remove the trailing new line
        return electrum_response
    except ConnectionRefusedError as e:
        print(e, server)
    except socket.gaierror as e:
        print(e, server)
    except Exception as e:
        print(e, server)
        return {'error': str(e)}



def pushtx(tx, testnet=False):
    """tx should be hex encoded"""
    #return sendtx(tx)
    return None  # disable for the moment

