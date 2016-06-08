# This Python file uses the following encoding: utf-8
import collections
import json
import re

import fowardZ
from flask_jsonrpc.exceptions import InvalidParamsError
from flask import request
from server_jsonrpc import jsonrpc
from common import convertToSeconds, hostExists, merge_two_dicts
from conf.config import cache_options, active_ro_instance

try:
    from uwsgi import cache_get, cache_set
except:
    def cache_get(*f):
        return None

    def cache_set(*f):
        return None

"""
@apiVersion 1.1.0
@apiGroup Generate
@apiName generateGraphs
@api {JSON-RPC} gbix.generateGraphs Gráficos
@apiDescription Retorna a url dos gráficos de itens e customizados de uma monitoração.
@apiParam {String} host Nome do host
@apiParam {String} [width] Largura do gráfico.
@apiParam {String} [height] Altura do gráfico.
@apiParam {String="s","m","h","d","w","M","a"} [period=3600] Caso passe apenas um número, a unidade de tempo default
 será a de segundos.
Caso contrário, deve ser passado um número acompanhado de um caractere que identifique o período.

Ex: "2d" = 2 dias ou "2" = 2 segundos.

s = Valor em segundos (unidade de tempo default).

m = Valor em minutos.

h = Valor em horas.

d = Valor em dias.

w = Valor em semanas.

M = Valor em meses.

y = Valor em anos.

@apiParam {Bool} [structured=false] Retorna os gráficos numa estrutura de objetos aninhandos. Recomendado o valor 'true'.

"""


@jsonrpc.method('gbix.generateGraphs')
def generateGraphs(host, structured=False, height=None, width=None, period=None):

    exist = hostExists(host)

    if not exist:
        raise InvalidParamsError('Host \'{0}\' not found.'.format(host))
    else:
        hostid = exist['hostid']
        return _generateGraphs(hostid, structured, height, width, period)


def _generateGraphs(hostid, structured=False, height=None, width=None, period=None):
    graphs_url, items_url = ({},) * 2

    """
    cached_graphs = cache_get('generateGraphs' + hostid, cache_all_name)
    cached_structured_graphs = cache_get('generateGraphs' + hostid + 'Struct', cache_all_name)

    if not structured and cached_graphs:
        return json.loads(cached_graphs)
    elif structured and cached_structured_graphs:
        return json.loads(cached_structured_graphs)
    """

    if active_ro_instance is True:
        url = active_ro_instance['fe_readonly_instance_url']
    else:
        url = request.url_root

    items = cache_get('itemGet?hostid='+hostid, cache_options['itemGet']['name'])

    if not items:
        items = fowardZ.sendToZabbix(method="item.get",
                                     params={'hostids': hostid,
                                             'output': ['name']})

        if 'result' in items:
            #print "Tamanho do resultado de items: ", sys.getsizeof(json.dumps(items)), "Bytes"
            cache_set('itemGet?hostid='+hostid, json.dumps(items), cache_options['itemGet']['expiration_time'],
                      cache_options['itemGet']['name'])
    else:
        items = json.loads(items)

    if 'result' in items:
        i = 0
        for item in items['result']:
            completeurl = url + 'chart.php?itemids=' + item['itemid']

            if period:
                seconds = convertToSeconds(period)
            else:
                seconds = '3600'

            completeurl = completeurl + '&period=' + seconds

            if width:
                completeurl = completeurl + '&width=' + width

            if height:
                completeurl = completeurl + '&height=' + height

            description = 'DirectGraph - ' + item['name']

            if description in items_url:
                items_url[description + ' ' + str(i)] = completeurl
                i += 1
            else:
                items_url[description] = completeurl
                i = 0

    graphs = cache_get('graphGet?hostid='+hostid, cache_options['graphGet']['name'])

    if not graphs:
        graphs = fowardZ.sendToZabbix(method="graph.get",
                                      params={'hostids': hostid,
                                              'expandName': '1',
                                              'output': ['name']})
        if 'result' in graphs:
            #print "Tamanho do resultado de graphs: ", sys.getsizeof(json.dumps(graphs)), "Bytes"
            cache_set('graphGet?hostid='+hostid, json.dumps(graphs), cache_options['graphGet']['expiration_time'],
                      cache_options['graphGet']['name'])
    else:
        graphs = json.loads(graphs)

    if 'result' in graphs:
        i = 0
        for graph in graphs['result']:

            completeurl = url + 'chart2.php?graphid=' + graph['graphid']

            if period:
                seconds = convertToSeconds(period)
            else:
                seconds = '3600'

            completeurl = completeurl + '&period=' + seconds

            if height:
                completeurl = completeurl + '&height=' + height

            if width:
                completeurl = completeurl + '&width=' + width

            description = 'UserGraph - ' + graph['name']
            if description in graphs_url:
                graphs_url[description + ' ' + str(i)] = completeurl
                i += 1
            else:
                graphs_url[description] = completeurl
                i = 0

    all_graphs = merge_two_dicts(items_url, graphs_url)
    #cache_set('genGraphs?hostid='+hostid, json.dumps(all_graphs), cache_expiration_time, cache_all_name)

    if structured:
        result2 = dict()
        for graph in all_graphs:
            if re.match("^UserGraph", graph):
                nome = re.sub('UserGraph - ', '', graph)
                #matches = re.match("^(.*) - (.*) - (.*)", nome)
                matches = re.match("([\w\s]+) - ([\w\s]+) - (.+)", nome)
                if matches is not None:
                    if matches.group(1) not in result2:
                        result2[matches.group(1)] = dict()
                    if matches.group(2) not in result2[matches.group(1)]:
                        result2[matches.group(1)][matches.group(2)] = dict()
                    if matches.group(3) not in result2[matches.group(1)][matches.group(2)]:
                        result2[matches.group(1)][matches.group(2)][matches.group(3)] = dict()
                    result2[matches.group(1)][matches.group(2)][matches.group(3)] = all_graphs[graph]
                else:
                    print 'Graph sem match: '+hostid+' - '+nome
        #cache_set('generateGraphs' + hostid + 'Struct', json.dumps(result2), cache_expiration_time, cache_all_name)
        return result2
    else:
        result = collections.OrderedDict(sorted(all_graphs.items()))  # checar como o usuario recebe este dict
        #cache_set('generateGraphs' + hostid, json.dumps(result), cache_expiration_time, cache_all_name)

        # print "Tamanho do resultado de graphs: ", sys.getsizeof(json.dumps(result)), "Bytes"
        return result

