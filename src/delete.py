# This Python file uses the following encoding: utf-8
from datetime import datetime

from flask_jsonrpc.exceptions import InvalidParamsError
from common import hostExists, n2i
from conf.definitions import GROUP_NOT_EXIST
from server_jsonrpc import jsonrpc
import fowardZ


"""
@apiVersion 1.1.0
@apiGroup Delete
@apiName deleteMonitors
@api {JSON-RPC} gbix.deleteMonitors Monitoração
@apiDescription Remove a monitoração de um host.
@apiParam {String} host Nome da monitoração.
"""
@jsonrpc.method('gbix.deleteMonitors')
def deleteMonitors(host):
    exist = hostExists(host)
    date = datetime.today().strftime('%y%m%d%H%M%S')

    if exist is not False:
        deleted_name = '_' + date + '_' + exist['name']
        deleted_host = '_' + date + '_' + exist['host']

        update = fowardZ.sendToZabbix(method="host.update", params={'hostid': exist['hostid'],
                                                                    'host': deleted_host,
                                                                    'name': deleted_name,
                                                                    'status': '1',
                                                                    'groups': [
                                                                        {'groupid': n2i.hostgroup(GROUP_NOT_EXIST)}
                                                                    ]})
        if 'result' in update:
            return 'Delete operation was successful'
        else:
            raise InvalidParamsError('It wasnt able to delete Host "{0}"'.format(host))
    else:
        raise InvalidParamsError('Host "{0}" doesnt exist.'.format(host))