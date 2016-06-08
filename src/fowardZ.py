import urllib2
import json

from flask import request
from flask_jsonrpc.helpers import extract_raw_data_request
from conf.config import endpointZ


header = {'Content-Type': 'application/json'}

def loadRequest(request_object):
    raw_data = extract_raw_data_request(request_object)
    return json.loads(raw_data)

def getAuth(request_object):
    data = loadRequest(request_object)
    return data['auth']

def getID(request_object):
    data = loadRequest(request_object)
    return data['id']


def sendToZabbix(method, params, endpoint=endpointZ, auth=None):
    if auth is None:
        auth = getAuth(request)

    ID = getID(request)

    if method == 'user.login':
        data = json.dumps(dict(jsonrpc='2.0', method=method, params=params, id=ID))
    else:
        data = json.dumps(dict(jsonrpc='2.0', method=method, params=params, auth=auth, id=ID))

    return sendRequest(data, endpoint)


def sendRequest(raw_data, endpoint=endpointZ):
    req = urllib2.Request(endpoint, data=raw_data, headers=header)
    response = urllib2.urlopen(req)
    result = response.read()
    result_json = json.loads(result)

    if 'result' in result_json:
        return {'result': result_json['result']}
    else:
        return {'error': result_json['error']}
