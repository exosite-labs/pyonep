#!/usr/bin/env python
#==============================================================================
# onep.py
# Main API library class for Exosite's Data Platform as exposed over HTTP JSON
# RPC
#==============================================================================
##
## Tested with python 2.6
##
## Copyright (c) 2010, Exosite LLC
## All rights reserved.
##
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2 smarttab

import sys,httplib
from onep_exceptions import *

try:
  if sys.version_info < (2 , 6):
    json_module= 'python-simplejson'
    import simplejson as json
  else:
    json_module= 'python-json'
    import json
except ImportError:
  print "The package '%s' is required." % json_module
  sys.exit(1)

#===============================================================================
class OnepV1():
#===============================================================================
  headers = {'Content-Type': 'application/json; charset=utf-8'}
  def __init__(self,host='m2.exosite.com',port='80',url='/api:v1/rpc/process',httptimeout=3,verbose=False):
    self.host        = host + ':' + port
    self.url         = url
    self.httptimeout = int(httptimeout)
    self._clientid   = None
    self._resourceid = None
    self.verbose     = verbose 

  def __callJsonRPC(self, clientkey, callrequests):
    auth = self.__getAuth(clientkey)
    jsonreq = {"auth":auth,"calls":callrequests}
    if sys.version_info < (2 , 6):
     conn = httplib.HTTPConnection(self.host)
    else:
     conn = httplib.HTTPConnection(self.host, timeout=self.httptimeout)
    param = json.dumps(jsonreq)
    if self.verbose: print("Request JSON: {0}".format(param))
    try:
      conn.request("POST", self.url, param, self.headers)
    except Exception:
      raise JsonRPCRequestException("Failed to make http request.")
    try:
      read = conn.getresponse().read()
    except Exception:
      if self.verbose: print sys.exc_info()[0]
      raise JsonRPCResponseException("Failed to get response of request.")
    try:
      res = json.loads(read)
      if self.verbose: print("Response JSON: {0}".format(res))
    except:
      raise OnePlatformException("Return invalid response value.")
    if isinstance(res,dict) and res.has_key('error'):
      raise OnePlatformException(str(res['error']))
    if isinstance(res,list) and len(res) > 0:
      if res[0].has_key('status'):
        if 'ok'  == res[0]['status']:
          if res[0].has_key('result'):
            return True,res[0]['result']
          return True,'ok'
        else:
          return False,res[0]['status']
      if res[0].has_key('error'):
        raise OnePlatformException(str(res[0]['error']))
    raise OneException("Unknown error")

  def __composeCall(self,method,argu):
    return [{"id":1,"procedure":method,"arguments":argu}]

  def __getAuth(self,clientkey):
    if None != self._clientid:
      return {"cik":clientkey,"client_id":self._clientid}
    elif None != self._resourceid:
      return {"cik":clientkey,"resource_id":self._resourceid}
    return {"cik":clientkey}

  def connect_as(self, clientid):
    self._clientid = clientid
    self._resourceid = None

  def connect_owner(self, resourceid):
    self._resourceid = resourceid
    self._clientid = None

  def __getattr__(self, name):
    return lambda *args, **kwargs: self.call_single(name, *args, **kwargs)

  def call_single(self, name, *args, **kwargs):
    if ARG_MAPPING.has_key(name):
      clientkey, arg = ARG_MAPPING[name](*args, **kwargs)
      request = self.__composeCall(name, arg)
      return self.__callJsonRPC(clientkey, request)
    else:
      raise AttributeError("No RPC method {0} defined".format(name))


# Functions that map arguments to clientkey, RPC argument pair
ARG_MAPPING = {
    'activate': lambda clientkey, codetype, code: 
      (clientkey, [codetype, code]),
    'comment': lambda clientkey, rid, visibility, comment:
      (clientkey, [rid, visibility, comment]),
    'create': lambda clientkey, type, desc:
      (clientkey, [type, desc]),
    'deactivate': lambda clientkey, codetype, code:
      (clientkey, [codetype, code]),
    'drop': lambda clientkey, rid:
      (clientkey, [rid]),
    'flush': lambda clientkey, rid:
      (clientkey, [rid]),
    'info': lambda clientkey, rid, options={}:
      (clientkey, [rid, options]),
    'listing': lambda clientkey, types:
      (clientkey, [types]),
    'lookup': lambda clientkey, type, mapping:
      (clientkey, [type, mapping]),
    'map': lambda clientkey, rid, alias:
      (clientkey, ['alias', rid, alias]),
    'read': lambda clientkey, rid, options:
      (clientkey, [rid, options]),
    'record': lambda clientkey, rid, entries, options={}:
      (clientkey, [rid, entries,options]),
    'revoke': lambda clientkey, codetype, code:
      (clientkey, [codetype, code]),
    'share': lambda clientkey, rid, options={}:
      (clientkey, [rid, options]),
    'unmap': lambda clientkey, alias:
      (clientkey, ['alias', alias]),
    'update': lambda clientkey, rid, desc={}:
      (clientkey, [rid, desc]),
    'write': lambda clientkey, rid, value, options={}:
      (clientkey, [rid, value, options]),
    'writegroup': lambda clientkey, entries, options={}:
      (clientkey, [entries, options]),
  }

def main(argv=None):
  if argv is None:
    argv = sys.argv
  onep = OnepV1(verbose=False)
  clientkey = 'f0cbd65a8d6ec75da52d91a48dfa6e6d05a8d68d'
  #clientkey = '20df3a8522b2d98834a7d2b36a7fccf4a087b5c6'
  print(onep.listing(clientkey, ['dataport']))
  options = {
      'starttime':1,
      'endtime':1000000000000,
      'limit':10,
      'sort':'desc',
      'selection':'all'
      }
  print(onep.read(clientkey, {'alias': 'sensor_a'}, options))
  
if __name__ == "__main__":
  sys.exit(main())
