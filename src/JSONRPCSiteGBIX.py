import fowardZ

from flask.wrappers import Response

from flask import json

from flask_jsonrpc.helpers import extract_raw_data_request
from flask_jsonrpc.exceptions import (InvalidRequestError,
                                      RequestPostError,
                                      Error,
                                      OtherError)

from flask_jsonrpc.site import JSONRPCSite
from  flask_jsonrpc.site import csrf_exempt

class JSONRPCSiteGBIX(JSONRPCSite):

    def __init__(self):
        super(JSONRPCSiteGBIX, self).__init__()
    
    @csrf_exempt
    def dispatch(self, request, method=''):
        # in case we do something json doesn't like, we always get back valid
        # json-rpc response
        response = self.empty_response()
        raw_data = extract_raw_data_request(request)

        try:
            if request.method == 'GET':
                valid, D = self.validate_get(request, method)
                if not valid:
                    raise InvalidRequestError('The method you are trying to access is '
                                              'not availble by GET requests')
            elif not request.method == 'POST':
                raise RequestPostError()
            else:
                try:
                    D = json.loads(raw_data)
                except Exception as e:
                    raise ParseError(getattr(e, 'message', e.args[0] if len(e.args) > 0 else None))

            if type(D) is list:
                return self.batch_response_obj(request, D)

            if D['method'].split('.')[0] != 'gbix':
                response = fowardZ.sendRequest(raw_data)
                status = 200
            else:
                response, status = self.response_obj(request, D)

            if isinstance(response, Response):
               return response, status

            if response is None and (not 'id' in D or D['id'] is None): # a notification
                response = ''
                return response, status
        except Error as e:
            response.pop('result', None)
            response['error'] = e.json_rpc_format
            status = e.status
        except Exception as e:
            other_error = OtherError(e)
            response.pop('result', None)
            response['error'] = other_error.json_rpc_format
            status = other_error.status

        # extract id the request
        if not response.get('id', False):
            json_request_id = self.extract_id_request(raw_data)
            response['id'] = json_request_id

        # If there was an error in detecting the id in the Request object
        # (e.g. Parse error/Invalid Request), it MUST be Null.
        if not response and 'error' in response:
            if response['error']['name'] in ('ParseError', 'InvalidRequestError', 'RequestPostError'):
                response['id'] = None

        return response, status


jsonrpc_site = JSONRPCSiteGBIX()