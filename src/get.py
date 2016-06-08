# This Python file uses the following encoding: utf-8
from datetime import datetime, timedelta

from flask_jsonrpc.exceptions import InvalidParamsError
from server_jsonrpc import jsonrpc
from common import addGroup, n2i
from admin import Admin
from conf.config import cache_options

try:
    from uwsgi import cache_get, cache_set, cache_update, cache_exists
except:
    def cache_get(*f):
        return None

    def cache_set(*f):
        return None

    def cache_update(*f):
        return None

    def cache_exists(*f):
        return None

import fowardZ
import json
import time


"""
@apiVersion 1.2.2
@apiGroup Get
@apiName getTriggers
@api {JSON-RPC} gbix.getTriggers Triggers
@apiDescription Busca triggers.

@apiParam {Array/String} [hosts=null] Nome do host.
@apiParam {Array/String} [hostgroups=null] Nome ou id do hostgroup.
@apiParam {String=0,1,2} withAck='2' '0' = Apenas trigger sem acknowledge.

 '1' = Apenas trigger com acknowledge.

 '2' = Todas as triggers.

@apiParam {Number} [maxAge=null] Inteiro indicando o tempo máximo de existência das triggers.
@apiParam {Array/String} [output="extend"] Quais atributos da trigger devem ser retornados.

 Ex:

 'extend' = Retorna todos os atributos

 ['triggerid', 'description'] = Retorna apenas o 'triggerid' e o 'description' da trigger.

 Todos atributos e suas descrições estão disponíveis <a href='https://www.zabbix.com/documentation/3.0/manual/api/reference/trigger/object'>aqui</a> .

"""
@jsonrpc.method('gbix.getTriggers')
def getTrigger(hosts=None, hostgroups=None, withAck=2, maxAge=None, lastChangeSince=None, lastChangeTill=None, output='extend'):

    extend = [
        'triggerid',
        'description',
        'expression',
        'comments',
        'error',
        'flags',
        'lastchange',
        'priority',
        'state',
        'status',
        'templateid',
        'type',
        'url',
        'value'
    ]

    triggers = getAllTriggersAlarming()
    triggers_the_user_will_see = list()

    hostgroups = addGroup(hostgroups)
    hostgroups[:] = [n2i.hostgroup(hostgroup) for hostgroup in hostgroups]

    hosts = addGroup(hosts)

    '''filtro por hosts'''
    if hosts:
        for trigger in triggers['result']:
            for host in trigger['hosts']:
                if host['name'] in hosts:
                    triggers_the_user_will_see.append(trigger)
    else:
        triggers_the_user_will_see = triggers['result']

    '''filtro por hostgroups'''
    if hostgroups:
        triggers_the_user_will_see[:] = [trigger for trigger in triggers_the_user_will_see for group in trigger['groups'] if group['groupid'] in hostgroups]

    '''filtro por ack'''
    withAck = str(withAck)
    if withAck not in ('0', '1', '2'):
        raise InvalidParamsError('Value {0} not permitted.'.format(withAck))
    else:
        if withAck == '2':
            pass
        elif withAck == '1':
            triggers_the_user_will_see[:] = [trigger for trigger in triggers_the_user_will_see if
                                             trigger['lastEvent'] and trigger['lastEvent']['acknowledged'] == '1']
        else:
            triggers_the_user_will_see[:] = [trigger for trigger in triggers_the_user_will_see if
                                             not trigger['lastEvent'] or
                                             trigger['lastEvent']['acknowledged'] == '0']

    '''filtro por data ~custom: por dias~'''
    if maxAge:
        since_date = datetime.now() - timedelta(maxAge)
        since_timestamp = time.mktime(since_date.timetuple())

        triggers_the_user_will_see[:] = [trigger for trigger in triggers_the_user_will_see if
                                         int(trigger['lastchange']) > since_timestamp]

    '''filtro por data a partir de'''
    if lastChangeSince:
       triggers_the_user_will_see[:] = [trigger for trigger in triggers_the_user_will_see if
                                        trigger['lastchange'] > lastChangeSince]

    '''filtro por data ate'''
    if lastChangeTill:
       triggers_the_user_will_see[:] = [trigger for trigger in triggers_the_user_will_see if
                                        trigger['lastchange'] < lastChangeTill]

    if output is not 'extend':
        for attribute in output:
            extend.remove(attribute)

        for trigger in triggers_the_user_will_see:
            for attribute in extend:
                trigger.pop(attribute)

    return triggers_the_user_will_see

def getAllTriggersAlarming():
    triggerCached = cache_get('triggerTelao', cache_options['triggerGet']['name'])
    if triggerCached:
        return json.loads(triggerCached)
    elif cache_get('updatingCache', cache_options['updates']['name']) == 'True':
        while cache_get('updatingCache', cache_options['updates']['name']) == 'True':
            time.sleep(0.3)
        else:
            return json.loads(cache_get('triggerTelao', cache_options['updates']['name']))
    else:
        if cache_exists('updatingCache', cache_options['updates']['name']):
            cache_update('updatingCache', 'True', cache_options['updates']['expiration_time'], cache_options['updates']['name'])
        else:
            cache_set('updatingCache', 'True', cache_options['updates']['expiration_time'], cache_options['updates']['name'])

        admin = Admin()
        zbx_admin_token = admin.auth()

        triggers = fowardZ.sendToZabbix(method='trigger.get', params={'selectHosts': ["name"],
                                                                      'selectGroups': ['groups'],
                                                                      'selectLastEvent': ['lastEvent',
                                                                                          'acknowledged'],
                                                                      'expandComment': 1,
                                                                      'expandDescription': 1,
                                                                      'only_true': 1,
                                                                      'output': 'extend'
                                                                      },
                                        auth=zbx_admin_token)

        cache_set('triggerTelao', json.dumps(triggers), cache_options['triggerGet']['expiration_time'], cache_options['triggerGet']['name'])
        cache_update('updatingCache', 'False', cache_options['updates']['expiration_time'], cache_options['updates']['name'])

    return triggers

"""
@jsonrpc.method('gbix.hostExists')
def hostExists(host):
    if not isinstance(host, basestring):
        raise InvalidParamsError('Host parameter must be a string.')

    result_host_get = fowardZ.sendToZabbix(method="host.get", params={'filter': {'name': host},
                                                                      #'selectMacros': 'extend',
                                                                      #'selectParentTemplates': 'templateid',
                                                                      #'selectGroups': 'groupid',
                                                                      'output': ['host', 'name', 'hostid'],
                                                                      'selectInterfaces': 'extend'},
                                           auth=None)

    if 'result' in result_host_get and result_host_get['result']:
        return result_host_get['result'][0]
    elif 'error' in result_host_get:
        raise InvalidParamsError('Error on check {0} existence.'.format(host))
    else:
        return False
"""