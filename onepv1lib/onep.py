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


class DeferredRequests():
  '''Encapsulates a list of deferred requests for each CIK. Once the requests
    are ready to be sent, get_method_args_pairs() returns a list of the method 
    name and arguments for each request.'''
  def __init__(self):
    self._requests = {}
  def add(self, cik, method, args):
    '''Append a deferred request for a particular cik.'''
    self._requests.setdefault(cik, []).append((method, args))
  def has_requests(self, cik):
    return (self._requests.has_key(cik) 
        and len(self._requests[cik]) > 0)
  def get_method_args_pairs(self, cik):
    return self._requests[cik]


class OnepV1():
  headers = {'Content-Type': 'application/json; charset=utf-8'}
  def __init__(self,host='m2.exosite.com',port='80',url='/api:v1/rpc/process',httptimeout=3,verbose=False):
    self.host        = host + ':' + port
    self.url         = url
    self.httptimeout = int(httptimeout)
    self._clientid   = None
    self._resourceid = None
    self.verbose     = verbose 
    self.deferred    = DeferredRequests() 

  def _callJsonRPC(self, cik, callrequests):
    '''Calls the Exosite One Platform RPC API.
      Returns'''
    auth = self._getAuth(cik)
    jsonreq = {"auth": auth, "calls": callrequests}
    if sys.version_info < (2, 6):
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
      raise JsonRPCResponseException("Failed to get response for request.")
    try:
      res = json.loads(read)
      if self.verbose: print("Response JSON: {0}".format(res))
    except:
      raise OnePlatformException("Return invalid response value.")
    if isinstance(res, dict) and res.has_key('error'):
      raise OnePlatformException(str(res['error']))
    if isinstance(res, list):
      ret = []
      for r in res:
        # first, find the matching request so we can return it 
        # along with the response.
        request = None
        for call in callrequests:
          if call['id'] == r['id']:
            request = call
        if r.has_key('status'):
          if 'ok'  == r['status']:
            if r.has_key('result'):
              ret.append((request, True, r['result']))
            else:
              ret.append((request, True, 'ok'))
          else:
            ret.append((request, False, r['status']))
        elif r.has_key('error'):
          raise OnePlatformException(str(r['error']))
      if len(ret) == 1:
        # backward compatibility: return just True/False and 'ok'/result/status
        # as before
        return ret[0][1:]
      else:
        return ret
    raise OneException("Unknown error")

  def _getAuth(self, cik):
    if None != self._clientid:
      return {"cik": cik, "client_id": self._clientid}
    elif None != self._resourceid:
      return {"cik": cik, "resource_id": self._resourceid}
    return {"cik": cik}

  def connect_as(self, clientid):
    self._clientid = clientid
    self._resourceid = None

  def connect_owner(self, resourceid):
    self._resourceid = resourceid
    self._clientid = None

  def __getattr__(self, name):
    if ARG_MAPPING.has_key(name):
      return lambda *args, **kwargs: self._call_single(name, *args, **kwargs)
    else:
      raise AttributeError

  def _call_single(self, method, *args, **kwargs):
    if ARG_MAPPING.has_key(method):
      defer = False
      if kwargs.has_key('defer'):
        # remove defer argument before passing to ARG_MAPPING
        defer = kwargs.pop('defer')

      cik, arg = ARG_MAPPING[method](*args, **kwargs)
      if defer:
        self.deferred.add(cik, method, arg)
        return True 
      else:
        calls = self._composeCalls([(method, arg)])
        return self._callJsonRPC(cik, calls)
    else:
      raise AttributeError("No RPC method {0} defined".format(method))

  def _composeCalls(self, method_args_pairs):
    calls = []
    i = 1 
    for method, args in method_args_pairs:
      calls.append({'id': i,
                    'procedure': method,
                    'arguments': args})
      i += 1
    return calls

  def send_deferred(self, cik):
    '''Send all deferred requests for a particular cik.'''
    if self.deferred.has_requests(cik):
      calls = self._composeCalls(self.deferred.get_method_args_pairs(cik))
    return self._callJsonRPC(cik, calls)

# Functions that map arguments to cik, RPC argument pair
ARG_MAPPING = {
    'activate': lambda cik, codetype, code:
      (cik, [codetype, code]),
    'comment': lambda cik, rid, visibility, comment:
      (cik, [rid, visibility, comment]),
    'create': lambda cik, type, desc:
      (cik, [type, desc]),
    'deactivate': lambda cik, codetype, code:
      (cik, [codetype, code]),
    'drop': lambda cik, rid:
      (cik, [rid]),
    'flush': lambda cik, rid:
      (cik, [rid]),
    'info': lambda cik, rid, options={}:
      (cik, [rid, options]),
    'listing': lambda cik, types:
      (cik, [types]),
    'lookup': lambda cik, type, mapping:
      (cik, [type, mapping]),
    'map': lambda cik, rid, alias:
      (cik, ['alias', rid, alias]),
    'read': lambda cik, rid, options:
      (cik, [rid, options]),
    'record': lambda cik, rid, entries, options={}:
      (cik, [rid, entries,options]),
    'revoke': lambda cik, codetype, code:
      (cik, [codetype, code]),
    'share': lambda cik, rid, options={}:
      (cik, [rid, options]),
    'unmap': lambda cik, alias:
      (cik, ['alias', alias]),
    'update': lambda cik, rid, desc={}:
      (cik, [rid, desc]),
    'write': lambda cik, rid, value, options={}:
      (cik, [rid, value, options]),
    'writegroup': lambda cik, entries, options={}:
      (cik, [entries, options]),
  }

