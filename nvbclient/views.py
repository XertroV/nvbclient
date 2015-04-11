from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    KeyStore,
    )

from .bitcoin import update_utxos


@view_config(route_name='update_utxos', renderer='templates/update_utxos.pt')
def update_utxos_view(request):
    update_utxos()
    return {'updating': True}


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(KeyStore).filter(KeyStore.name == 'primary').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'name': one.name, 'project': 'nvb-client'}


@view_config(route_name='key_details', renderer='templates/key_details.pt')
def key_details_view(request):
  return {'keys': DBSession.query(KeyStore).all()}


@view_config(route_name='admin', renderer='templates/admin.pt')
def admin_view(request):
    return {}

@view_config(route_name='initialize_network', renderer='templates/dump_dict.pt')
def admin_initialize_network_view(request):

    return {'dict': {}}

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

