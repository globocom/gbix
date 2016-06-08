# **GBIX**
---
GBIX is a wrapper for Zabbix API. 

## How it works?
---
GBIX extends [flask_jsonrpc](https://github.com/cenobites/flask-jsonrpc) module (thanks, [Cenobit](https://github.com/cenobites)! :) , but instead of working only as JSON-RPC Server, it also fowards all 
requests destinated to Zabbix API to your Zabbix instance (eg. its native methods). So you can create your own methods, manipulate
every data and work apart Zabbix Frontend. 

## Starting your app
---
```bash
$ cd src/
$ python server_jsonrpc.py
```

## Hello, gbix!
---
```bash
$curl -H "Content-Type:application/json"  -X POST \
    -d '{ "id": 1,
          "jsonrpc": "2.0",
          "method": "gbix.hello",
          "params":{} }' http://localhost:81/api
HTTP/1.1 200 OK
Server: nginx/1.6.3
Date: Wed, 25 May 2016 21:41:48 GMT
Content-Type: application/json
Content-Length: 90
Connection: keep-alive

{
  "id": 1, 
  "jsonrpc": "2.0", 
  "result": "Welcome to GBIX, an API JSON-RPC based."
}
```

## Avaible methods
---
* POST /api
    * gbix.hello  
    * gbix.createLinuxMonitors    
    * gbix.deleteMonitors
    * gbix.disableMonitors
    * gbix.disableAlarms
    * gbix.enableAlarms
    * gbix.enableMonitors
    * gbix.generateGraphs
    * gbix.getTriggers
* GET /api
    * /healthcheck 
    
## Fork us!
---
Fork us and create your own methods for Zabbix! 

## Referencies
---
* http://docs.python.org/
* https://github.com/cenobites/flask-jsonrpc
* http://flask.pocoo.org/docs/
* http://www.jsonrpc.org/

## Dependecies
---

Flask-JSONRPC (0.3) (https://github.com/cenobites/flask-jsonrpc)