# This Python file uses the following encoding: utf-8
import re

from server_jsonrpc import jsonrpc
from common import addGroup, hostExists, n2i
from conf.definitions import *
from disable import disableAlarms
from flask_jsonrpc import InvalidParamsError
from generate import generateGraphs
import fowardZ


def createMonitor(returning_graphs, monitor_type, hostname, visible_name, ip, proxy=None, groups=None,
                  templates=None, macros=None, inventory=None):
    if groups is None:
        groups = []

    if templates is None:
        templates = []

    if macros is None:
        macros = {}

    templates_structure = []
    groups_structure = []
    macros_structure = []

    for template in templates:
        templates_structure.append({'templateid': n2i.template(template)})

    for group in sorted(set(groups)):
        groups_structure.append({'groupid': n2i.hostgroup(group)})

    for macro, value in macros.iteritems():
        if value is not None:
            macros_structure.append({'macro': macro, 'value': value})

    if monitor_type == 'snmp':
        interfaces_structure = [{'type': '2',  # snmp
                                 'main': '1',
                                 'useip': '1',
                                 'ip': ip,
                                 'dns': '',
                                 'port': SNMP_PORT
                                 }]
    elif monitor_type == 'agent':
        if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) is not None:
            interfaces_structure = [{'type': '1',  # agent
                                     'main': '1',
                                     'useip': '1',
                                     'ip': ip,
                                     'dns': '',
                                     'port': AGENT_PORT
                                     }]
        else:
            interfaces_structure = [{'type': '1',  # agent
                                     'main': '1',
                                     'useip': '0',
                                     'ip': '',
                                     'dns': ip,
                                     'port': AGENT_PORT
                                     }]
    else:
        raise InvalidParamsError('Monitoring type \'{0}\' not supported.'.format(monitor_type))


    exist = hostExists(visible_name) if visible_name else hostExists(hostname)

    # exist = hostExists(visible_name)

    proxy = n2i.proxy(proxy)

    if not exist:
        create = fowardZ.sendToZabbix(method="host.create",
                                      params={
                                          'host': hostname,
                                          'name': visible_name,
                                          'interfaces': interfaces_structure,
                                          'proxy_hostid': proxy,
                                          'groups': groups_structure,
                                          'templates': templates_structure,
                                          'macros': macros_structure,
                                          'inventory': inventory}
                                      )
    else:
        raise InvalidParamsError('"{0}" already exists in Zabbix Database.'.format(hostname))

    if 'result' in create:
        if returning_graphs == 'returnallgraphs':
            graphs = generateGraphs(visible_name) if visible_name else generateGraphs(hostname)
            if graphs:
                return graphs
            else:
                return 'Create operation was successful, but there are no graphs to show.'
        elif returning_graphs == 'defaultreturn':
            return 'Create operation was successful'
        else:
            return create
    else:
        raise InvalidParamsError(create['error']['data'])


"""
@apiVersion 1.2.1
@apiGroup Create
@apiName createBasicMonitors
@api {JSON-RPC} gbix.createBasicMonitors Básico
@apiDescription Cria monitoração básica de vitais (monitoracao do sistema operacional) para um host linux.

@apiParam {String} host Nome do host.
@apiParam {String} ip IP do host.
@apiParam {String[]} [clientgroup=null] Nome ou id do(s) hostgroup(s) para associar a monitoração.
@apiParam {String="yes","no","group"} [alarm=group] Opção de alarme:

yes = Alarma para a equipe de Operação + grupo.

no = Não alarma.

group = Alarma grupo.
@apiParam {String} [zbx_proxy='NOME_DO_PROXY'] Proxy de coleta do Zabbix.
"""


@jsonrpc.method('gbix.createBasicMonitors')
def createBasicMonitors(host, ip, alarm='group', zbx_proxy=None, clientgroup=None):
    if clientgroup is None:
        clientgroup = []

    groups, templates, disable = (None,) * 3

    if alarm == 'yes':
        groups = addGroup([GROUP_OSLINUX, GROUP_API, GROUP_OP, GROUP_OP_SERVIDOR], groups)
    elif alarm == 'group':
        groups = addGroup([GROUP_OSLINUX, GROUP_API], groups)
    elif alarm == 'no':
        groups = addGroup([GROUP_OSLINUX, GROUP_API], groups)
        disable = True
    else:
        raise InvalidParamsError('Alarm option "{0}" is not supported.'.format(alarm))

    if zbx_proxy is None:
        zbx_proxy = PRX_DEFAULT

    groups = addGroup(clientgroup, groups)
    templates = addGroup([TEMPLATE_VT], templates)

    basic = createMonitor('defaultreturn', 'snmp', host, host, ip, zbx_proxy, groups, templates)

    if disable is True:
        disableAlarms(host)

    return basic

