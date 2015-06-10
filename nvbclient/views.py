import json

from binascii import hexlify, unhexlify

from pycoin.encoding import EncodingError

from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
from pyramid.response import Response

from nvblib import instruction_lookup

from .models import (
    DBSession,
    KeyStore,
    )

from .bitcoin import update_utxos, total_balance, make_signed_tx_from_vote, addr_to_testnet

from .auth import check_password, get_private_bytes, set_private_bytes, get_key_store


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


def disable_when_demo(f):
    def inner(request, *args, **kwargs):
        if request.registry.settings['demo_mode'] != "false":
            return {'result': False, 'message': 'Disabled in demo mode.'}
        return f(request, *args, **kwargs)
    return inner


def only_when_demo(f):
    def inner(request, *args, **kwargs):
        if request.registry.settings['demo_mode'] != "true":
            raise Exception('Only enabled in demo mode.')
        return f(request, *args, **kwargs)
    return inner


# old method of enabling demo, can be done via config
saved_password = b'1234567890987654321234567890987654345678'


@view_config(route_name='empower_demo_start', renderer='json')
@only_when_demo
@auth
def empower_demo_start_view(request):
    global saved_password
    saved_password = pw_from_r(request)
    print('Enabling Empower Demo')
    return {'result': saved_password.decode()}


already_empowered = {}
@view_config(route_name='empower_demo')
@only_when_demo
def empower_demo_view(request):
    global saved_password
    address = request.json_body['address']
    if address not in already_empowered:
        op = instruction_lookup('empower')(1000, address)
        if 'demo_password' in request.registry.settings:
            saved_password = request.registry.settings['demo_password'].encode()
        already_empowered[address] = make_signed_tx_from_vote(op, saved_password, extra_payables=[(op.address_pretty(), 50000)]).as_hex()
    response = Response(json.dumps({'result': already_empowered[address]}), content_type='applicatoin/json', charset='utf8')
    response.headerlist.append(('Access-Control-Allow-Origin', '*'))
    return response



@view_config(route_name='demo_test', renderer='json')
def demo_test_view(request):
    return {'result': request.registry.settings['demo_mode'] != "false"}


@view_config(route_name='update_utxos', renderer='json')
@auth
def update_utxos_view(request):
    n_utxos = update_utxos()
    balance = total_balance()
    return {'updated': True, 'n_utxos': n_utxos, 'balance': balance}


@view_config(route_name='home', renderer='templates/index.pt')
def my_view(request):
    return {}


@view_config(route_name='key_details', renderer='json')
@auth  # maybe this prevents information leaking?
def key_details_view(request):
  return {'keys': [dict([(k, str(v)) if type(v) != bytes else (k, hexlify(v).decode()) for k,v in d.__dict__.items()]) for d in DBSession.query(KeyStore).all()]}


@view_config(route_name='check_password', renderer='json')
def check_password_view(request):
    password = pw_from_r(request)
    pw_correct = check_password(password)
    address = get_key_store().address
    if pw_correct:
        return {'result': pw_correct, 'address': address, 'testnet_address': addr_to_testnet(address)}
    return {'result': False}

@view_config(route_name='change_password', renderer='json')
@disable_when_demo
@auth
def change_password_view(request):
    if request.registry.settings['demo_mode'] != "false":
        return {'result': False, 'message': 'Password change disabled in demo mode.'}
    old_password = pw_from_r(request)
    new_password = pw_from_r(request, 'new_password')
    try:
        set_private_bytes(new_password, get_private_bytes(old_password))
    except Exception as e:
        return {'result': False, 'message': 'Password change failed: %s' % e}
    return {'result': True, 'message': 'Changed Password Successfully'}


@view_config(route_name='sign_vote', renderer='json')
@auth
def sign_vote_view(request):
    rjb = request.json_body
    assert 'vote' in rjb
    try:
        vote = instruction_lookup(rjb['vote']['type'])(**rjb['vote']['params'])
    except EncodingError as e:
        return {'result': False, 'msg': "Bad Address? -- " + str(e)}
    stx = make_signed_tx_from_vote(vote, pw_from_r(request))
    return {'result': True, 'msg': stx.as_hex()}

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

