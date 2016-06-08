# This Python file uses the following encoding: utf-8
from common import hostExists
from server_jsonrpc import jsonrpc
from flask_jsonrpc.exceptions import InvalidParamsError

import fowardZ


"""
@apiVersion 1.1.0
@apiGroup Disable
@apiName disableMonitors
@api {JSON-RPC} gbix.disableMonitors Monitoração
@apiDescription Desabilita um host no Zabbix.
@apiParam {String} host Nome do host no Zabbix.
"""
@jsonrpc.method('gbix.disableMonitors')
def disableMonitors(host):
    exist = hostExists(host)
    if exist is not False:
        update = fowardZ.sendToZabbix(method='host.update', params={'hostid': exist['hostid'],
                                                                    'status': '1'})
        if 'result' in update:
            return 'Disable operation was successful.'
        else:
            raise InvalidParamsError('It wasnt able to disable monitors on host "{0}"'.format(host))
    else:
        raise InvalidParamsError('Host "{0}" doesnt exist.'.format(host))


"""
@apiVersion 1.1.0
@apiGroup Disable
@apiName disableAlarms
@api {JSON-RPC} gbix.disableAlarms Alarmes
@apiDescription Desabilita os alarmes de um host no Zabbix.
@apiParam {String} host Nome do host no Zabbix.
"""
@jsonrpc.method('gbix.disableAlarms')
def disableAlarms(host):
    exist = hostExists(host)

    if exist is not False:
        return _disableAlarms(exist['hostid'])
    else:
        raise InvalidParamsError('Host "{0}" not found.'.format(host))


def _disableAlarms(hostid):

    trigger_get = fowardZ.sendToZabbix(method='trigger.get', params={'hostids': hostid,
                                                                     'output': 'triggerid'})

    triggerPrototype_get = fowardZ.sendToZabbix(method='triggerprototype.get', params={'hostids':hostid,
                                                                                       'output':'triggerid'})

    triggers = []
    triggersPrototype = []

    for trigger in trigger_get['result']:
        triggers.append({'triggerid': trigger['triggerid'], 'status': '1'})

    disabled = fowardZ.sendToZabbix(method='trigger.update', params=triggers)

    disabledPrototype = dict(result = True)
    if triggerPrototype_get:
        for triggerPrototype in triggerPrototype_get['result']:
            triggersPrototype.append({'triggerid': triggerPrototype['triggerid'], 'status':'1'})

        disabledPrototype = fowardZ.sendToZabbix(method='triggerprototype.update', params=triggersPrototype)


    if 'result' in disabled and 'result' in disabledPrototype:
        return 'Disable operation was successful.'
    else:
        raise InvalidParamsError('It wasnt able to disable alarms on hostid "{0}"'.format(hostid))
