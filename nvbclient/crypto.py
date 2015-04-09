from base64 import b64encode

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

''' THIS FILE IS NOT WHERE MOST CRYPTO SHOULD GO!
Most crypto used in nvb-client will be imported from the `cryptography` library.
It should be included and used directly, not through this file. This is so the
cryptography used is a) plain to see and b) able to be reasoned about in the
correct context. Only on rare occasions should something from this file be
imported in order to maintain consistency.

A minimum number of cryptographic primitives should be used to achieve ease of
audit if the time comes.
'''

# check calling this when the module is loaded is not insecure
backend = default_backend()

def kdf_from_salt(salt: bytes):
  return PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=backend
  )

def make_key(kdf, password: bytes):
  return kdf.derive(password)

def gen_key_from_salt_and_password(salt, password):
  # keys in `cryptography` are base64
  return b64encode(make_key(kdf_from_salt(salt), b''))

