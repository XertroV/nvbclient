import json

from binascii import hexlify, unhexlify

from pyramid.httpexceptions import HTTPForbidden

from pyramid.response import Response
from pyramid.view import view_config

from cryptography.fernet import Fernet

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    KeyStore,
    )

from .bitcoin import update_utxos, total_balance, make_signed_tx_from_vote

from .auth import check_password, get_private_bytes, set_private_bytes, get_key_store

from .constants import PRIMARY

from .nvb_instructions import Instruction, NewNetwork, instruction_lookup

def prep_json_dump(d):
    return {'to_dump': d, 'json': json}

def pw_from_r(r, i='password'):
    return bytes(r.json_body[i].encode())


def auth(f):
    def inner(request, *args, **kwargs):
        if not hasattr(request, 'json_body') or 'password' not in request.json_body:
            raise HTTPForbidden('Password Required')
        if not check_password(pw_from_r(request)):
            raise HTTPForbidden('Password Incorrect')
        return f(request, *args, **kwargs)
    return inner


@view_config(route_name='update_utxos', renderer='templates/json.pt')
@auth
def update_utxos_view(request):
    n_utxos = update_utxos()
    balance = total_balance()
    return prep_json_dump({'updated': True, 'n_utxos': n_utxos, 'balance': balance})


@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
    return {}


@view_config(route_name='key_details', renderer='templates/json.pt')
@auth  # maybe this prevents information leaking?
def key_details_view(request):
  return prep_json_dump({'keys': [dict([(k, str(v)) if type(v) != bytes else (k, hexlify(v).decode()) for k,v in d.__dict__.items()]) for d in DBSession.query(KeyStore).all()]})


@view_config(route_name='initialize_network', renderer='templates/json.pt')
@auth
def admin_initialize_network_view(request):
    return prep_json_dump({'tx': ''})

@view_config(route_name='check_password', renderer='templates/json.pt')
def check_password_view(request):
    password = pw_from_r(request)
    pw_correct = check_password(password)
    if pw_correct:
        return prep_json_dump({'result': pw_correct, 'address': get_key_store().address})
    return prep_json_dump({'result': False})

@view_config(route_name='change_password', renderer='templates/json.pt')
@auth
def change_password_view(request):
    old_password = pw_from_r(request)
    new_password = pw_from_r(request, 'new_password')
    try:
        set_private_bytes(new_password, get_private_bytes(old_password))
    except Exception as e:
        return prep_json_dump({'result': False, 'message': 'Password change failed: %s' % e})
    return prep_json_dump({'result': True, 'message': 'Changed Password Successfully'})


@view_config(route_name='sign_vote', renderer='templates/json.pt')
@auth
def sign_vote_view(request):
    rjb = request.json_body
    print(rjb)
    vote = instruction_lookup(rjb['vote']['type'])(**rjb['vote']['params'])
    stx = make_signed_tx_from_vote(vote, pw_from_r(request))
    #import pdb; pdb.set_trace()
    return prep_json_dump({'result': True, 'tx': stx.as_hex()})

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_nvb-client_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

