# This Python file uses the following encoding: utf-8
from server_jsonrpc import jsonrpc
from common import hostExists
from flask_jsonrpc.exceptions import InvalidParamsError

import fowardZ

"""
@apiVersion 1.1.0
@apiGroup Enable
@apiName enableMonitors
@api {JSON-RPC} gbix.enableMonitors Monitoração
@apiDescription Habilita um host no Zabbix.
@apiParam {String} host Nome do host no Zabbix.
"""
@jsonrpc.method('gbix.enableMonitors')
def enableMonitors(host):
    exist = hostExists(host)
    if exist is not False:
        update = fowardZ.sendToZabbix(method='host.update', params={'hostid': exist['hostid'],
                                                                    'status': '0'})
        if 'result' in update:
            return 'Enable operation was successful.'
        else:
            raise InvalidParamsError('It wasnt able to enable monitors on host "{0}"'.format(host))
    else:
        raise InvalidParamsError('Host "{0}" doesnt exist.'.format(host))


"""
@apiVersion 1.1.0
@apiGroup Enable
@apiName enableAlarms
@api {JSON-RPC} gbix.enableAlarms Alarmes
@apiDescription Habilita os alarmes de um host no Zabbix.
@apiParam {String} host Nome do host no Zabbix.
"""
@jsonrpc.method('gbix.enableAlarms')
def enableAlarms(host):
    exist = hostExists(host)
    if exist is not False:
        trigger_get = fowardZ.sendToZabbix(method='trigger.get', params={'hostids': exist['hostid'],
                                                                         'output': 'triggerid'})
        triggerPrototype_get = fowardZ.sendToZabbix(method='triggerprototype.get', params={'hostids': exist['hostid'],
                                                                                           'output': 'triggerid'})

        triggers = list()
        triggersPrototype = list()

        for trigger_host in trigger_get['result']:
            triggers.append({'triggerid': trigger_host['triggerid'], 'status': '0'})

        enabled = fowardZ.sendToZabbix(method='trigger.update', params=triggers)

        enabledPrototype = dict(result = True)
        if triggerPrototype_get:
            for triggerPrototype in triggerPrototype_get['result']:
                triggersPrototype.append({'triggerid': triggerPrototype['triggerid'], 'status':'0'})

            enabledPrototype = fowardZ.sendToZabbix(method='triggerprototype.update', params=triggersPrototype)

        if 'result' in enabled and 'result' in enabledPrototype:
            return 'Enable operation was successful.'
        else:
            raise InvalidParamsError('It wasnt able to enable alarms on host "{0}"'.format(host))

    else:
        raise InvalidParamsError('Host "{0}" doesnt exist.'.format(host))
