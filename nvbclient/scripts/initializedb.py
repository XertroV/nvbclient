import os
import sys
import transaction
from cryptography.fernet import Fernet
from base64 import b64encode

from pycoin.key import Key

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    KeyStore,
    Base,
    )

from ..util import convert_se_bytes

from ..crypto import gen_key_from_salt_and_password

from ..constants import ENDIAN, USE_COMPRESSED, PRIMARY

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    
    # initial encryption passphrase set to ''
    salt = os.urandom(32)

    password = bytes(input("If you would like to set a password, please enter it now. Otherwise, just press enter. > ").encode())
    
    # initial password is the empty string
    enc_key = gen_key_from_salt_and_password(salt, password)
    f = Fernet(enc_key)

    secret_exponent_bytes = os.urandom(32)
    secret_exponent = convert_se_bytes(secret_exponent_bytes)
    address = Key(secret_exponent=secret_exponent).address(use_uncompressed=USE_COMPRESSED)

    with transaction.manager:
        model = KeyStore(name=PRIMARY, encrypted=f.encrypt(secret_exponent_bytes),
                         salt=salt, address=address)
        DBSession.add(model)
