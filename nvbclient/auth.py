from cryptography.fernet import Fernet, InvalidToken

from pycoin.key import Key

from .crypto import gen_key_from_salt_and_password

from .constants import PRIMARY

from .models import (
    DBSession,
    KeyStore,
)

from .util import convert_se_bytes


def get_key_store(user=PRIMARY):
    return DBSession.query(KeyStore).filter(KeyStore.name == user).first()


def get_private_bytes(password, user=PRIMARY):
    key_store = get_key_store(user)
    salt = key_store.salt
    encrypted_privkey = key_store.encrypted
    f = Fernet(gen_key_from_salt_and_password(salt, password))
    try:
        decrypted_bytes = f.decrypt(encrypted_privkey)
    except InvalidToken:
        return None
    return decrypted_bytes


def set_private_bytes(password, decrypted_bytes, user=PRIMARY):
    pks = prev_key_store = get_key_store(user)
    f = Fernet(gen_key_from_salt_and_password(pks.salt, password))
    DBSession.merge(KeyStore(id=pks.id, name=pks.name, encrypted=f.encrypt(decrypted_bytes), salt=pks.salt, address=pks.address))


def get_private_key(password, user=PRIMARY):
    decrypted_bytes = get_private_bytes(password, user)
    if decrypted_bytes is None:
        return None
    private_key = Key(secret_exponent=convert_se_bytes(decrypted_bytes))
    return private_key


def check_password(password, user=PRIMARY):
    return get_private_key(password, user) is not None