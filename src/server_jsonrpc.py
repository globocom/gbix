# This Python file uses the following encoding: utf-8
import socket
import os
import re

import fowardZ
from flask import Flask
from flask_jsonrpc import JSONRPC
from conf.config import cache_options
from JSONRPCSiteGBIX import jsonrpc_site


try:
    from uwsgi import cache_get, cache_set
except:
    def cache_get(*f):
        return None

    def cache_set(*f):
        return None

app = Flask(__name__)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=False, site=jsonrpc_site)

@app.route('/api/healthcheck')
def healthcheck():
    fe_status_cached = cache_get('gbix_healthcheck', cache_options['default']['name'])

    if fe_status_cached:
        return fe_status_cached

    else:
        try:
            fe_status = fowardZ.sendRequest('{"jsonrpc": "2.0", \
                                        "method": "apiinfo.version", \
                                        "params": [], \
                                        "id": 1 \
                                        }')
        except:
            status_string = 'FAILED ' + socket.gethostname() + ' Sem conexao com o FE do Zabbix'
            cache_set('gbix_healthcheck', status_string, 3, cache_options['default']['name'])
            return status_string

        if 'result' in fe_status:
                status_string = 'WORKING ' + socket.gethostname()
                cache_set('gbix_healthcheck', status_string, 5, cache_options['default']['name'])
                return status_string
        else:
            status_string = 'FAILED ' + socket.gethostname() + 'Sem conexao com o FE do Zabbix'
            cache_set('gbix_healthcheck', status_string, 3, cache_options['default']['name'])
            return status_string


@app.route('/api/methods')
def methods():

    gbix_methods_cached = cache_get('/api/methods', cache_options['default']['name'])

    if not gbix_methods_cached:
        try:
            arq = os.path.join(os.path.split(os.path.split(os.path.realpath(__file__))[0])[0], 'doc/api_data.json')
            f = open(arq)
        except IOError:
            return 'Methods file not found.'
        methods_json = str()
        pattern = re.compile('\s+"filename')
        for line in f.readlines():
            if re.match(pattern, line) is None:
                methods_json += line.strip().replace('<p>', '').replace('</p>', '').replace(' "', '"').replace('\\"', '')
        f.close()
        cache_set('/api/methods', methods_json, 0, cache_options['default']['name'])
        return methods_json
    else:
        return gbix_methods_cached



@jsonrpc.method('gbix.hello')
def index():
    return 'Welcome to GBIX, an API JSON-RPC based.'

import common
import delete
import enable
import create
import disable
import generate
import get

if __name__ == '__main__':
    app.run(host='localhost', debug=True)
