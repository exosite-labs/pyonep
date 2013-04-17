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
    '''Append a deferred request for a particular CIK.'''
    self._requests.setdefault(cik, []).append((method, args))
  def reset(self, cik):
    self._requests.pop(cik)
  def has_requests(self, cik):
    '''Returns True if there are any deferred requests for CIK, False
    otherwise.'''
    return (self._requests.has_key(cik)
        and len(self._requests[cik]) > 0)
  def get_method_args_pairs(self, cik):
    '''Returns a list of method/arguments pairs corresponding to deferred
    requests for this CIK'''
    return self._requests[cik]


class OnepV1():
  headers = {'Content-Type': 'application/json; charset=utf-8'}
  def __init__(self,host='logicpd.m2.exosite.com',port='80',url='/api:v1/rpc/process',httptimeout=3,verbose=False):
    self.host        = host + ':' + port
    self.url         = url
    self.httptimeout = int(httptimeout)
    self._clientid   = None
    self._resourceid = None
    self.verbose     = verbose
    self.deferred    = DeferredRequests()
    self.api = [
        self.activate,
        self.comment,
        self.create,
        self.deactivate,
        self.drop,
        self.flush,
        self.info,
        self.listing,
        self.lookup,
        self.map,
        self.read,
        self.record,
        self.revoke,
        self.share,
        self.unmap,
        self.update,
        self.write,
        self.writegroup,
        ]

  def _callJsonRPC(self, cik, callrequests, returnreq=False, showhttp=False):
    '''Calls the Exosite One Platform RPC API.
      If returnreq is False, result is a tuple with this structure:
        (success (boolean), response)

      If returnreq is True, result is a list of tuples with
      this structure:
        (request, success, response)
        '''
    auth = self._getAuth(cik)
    jsonreq = {"auth": auth, "calls": callrequests}
    if sys.version_info < (2, 6):
      conn = httplib.HTTPConnection(self.host)
    else:
      conn = httplib.HTTPConnection(self.host, timeout=self.httptimeout)
    param = json.dumps(jsonreq)
    if self.verbose: print("Request JSON: {0}".format(param))
    try:

      if showhttp: print("POST {}\nBody: {}\nHeaders: {}".format(self.url, param, self.headers))
      conn.request("POST", self.url, param, self.headers)
    except Exception:
      raise JsonRPCRequestException("Failed to make http request.")
    try:
      read = conn.getresponse().read()
      if showhttp: print("Response: {}".format(read))
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
      if returnreq:
        return ret
      else:
        # backward compatibility: return just True/False and
        # 'ok'/result/status as before
        return ret[0][1:]

    raise OneException("Unknown error")

  def _getAuth(self, cik):
    '''Create the authorization/identification portion of a request.'''
    if None != self._clientid:
      return {"cik": cik, "client_id": self._clientid}
    elif None != self._resourceid:
      return {"cik": cik, "resource_id": self._resourceid}
    return {"cik": cik}

  def _composeCalls(self, method_args_pairs):
    calls = []
    i = 1
    for method, args in method_args_pairs:
      calls.append({'id': i,
                    'procedure': method,
                    'arguments': args})
      i += 1
    return calls

  def _call(self, method, cik, arg, defer):
    if defer:
      self.deferred.add(cik, method, arg)
      return True
    else:
      calls = self._composeCalls([(method, arg)])
      return self._callJsonRPC(cik, calls)

  def has_deferred(self, cik):
    return self.deferred.has_requests(cik)

  def send_deferred(self, cik):
    '''Send all deferred requests for a particular cik.'''
    if self.deferred.has_requests(cik):
      calls = self._composeCalls(self.deferred.get_method_args_pairs(cik))
      r = self._callJsonRPC(cik, calls, returnreq=True)
      # remove deferred calls
      self.deferred.reset(cik)
      return r
    raise JsonRPCRequestException('No deferred requests to send.')

  def connect_as(self, clientid):
    self._clientid = clientid
    self._resourceid = None

  def connect_owner(self, resourceid):
    self._resourceid = resourceid
    self._clientid = None

  # API methods

  def activate(self, cik, codetype, code, defer=False):
    return self._call('activate', cik, [codetype, code], defer)

  def comment(self, cik, rid, visibility, comment, defer=False):
    return self._call('comment', cik, [rid, visibility, comment], defer)

  def create(self, cik, type, desc, defer=False):
    return self._call('create', cik, [type, desc], defer)

  def deactivate(self, cik, codetype, code, defer=False):
    return self._call('deactivate', cik, [codetype, code], defer)

  def drop(self, cik, rid, defer=False):
    return self._call('drop', cik, [rid], defer)

  def flush(self, cik, rid, defer=False):
    return self._call('flush', cik, [rid], defer)

  def info(self, cik, rid, options={}, defer=False):
    return self._call('info', cik,  [rid, options], defer)

  def listing(self, cik, types, defer=False):
    return self._call('listing', cik, [types], defer)

  def lookup(self, cik, type, mapping, defer=False):
    return self._call('lookup', cik, [type, mapping], defer)

  def map(self, cik, rid, alias, defer=False):
    return self._call('map', cik, ['alias', rid, alias], defer)

  def read(self, cik, rid, options, defer=False):
    return self._call('read', cik, [rid, options], defer)

  def record(self, cik, rid, entries, options={}, defer=False):
    return self._call('record', cik, [rid, entries,options], defer)

  def revoke(self, cik, codetype, code, defer=False):
    return self._call('revoke', cik, [codetype, code], defer)

  def share(self, cik, rid, options={}, defer=False):
    return self._call('share', cik, [rid, options], defer)

  def unmap(self, cik, alias, defer=False):
    return self._call('unmap', cik, ['alias', alias], defer)

  def update(self, cik, rid, desc={}, defer=False):
    return self._call('update', cik, [rid, desc], defer)

  def write(self, cik, rid, value, options={}, defer=False):
    return self._call('write', cik, [rid, value, options], defer)

  def writegroup(self, cik, entries, options={}, defer=False):
    return self._call('writegroup', cik, [entries, options], defer)


  # High level commands
  # (Built on top of API)

  def create_dataport(self,
                      cik,
                      format,
                      name="",
                      preprocess=[],
                      retention={"count":"infinity","duration":"infinity"},
                      subscribe="",
                      visibility="private",
                      defer=False):
    desc = {
        "format": format,
        "name": name,
        "preprocess": preprocess,
        "retention": retention,
        "subscribe": subscribe,
        "visibility": visibility
        }
    return self.create(cik, type='dataport', desc=desc, defer=defer)

  class Rule():
    '''Collection of rule generation methods for create_datarule().'''

    @classmethod
    def simple(cls, comparison, constant, repeat):
      return {"simple": {
                "comparison": comparison,
                "constant": constant,
                "repeat": repeat}
                }

    @classmethod
    def timeout(cls, repeat, timeout):
      return {"timeout": {
                "repeat": repeat,
                "timeout": timeout}
                }

    @classmethod
    def interval(cls, comparison, constant, repeat, timeout):
      return {"interval": {
                "comparison": comparison,
                "constant": constant,
                "repeat": repeat,
                "timeout": timeout}
                }

    @classmethod
    def duration(cls, comparison, constant, repeat, timeout):
      return {"duration": {
                "comparison": comparison,
                "constant": constant,
                "repeat": repeat,
                "timeout": timeout}
                }

    @classmethod
    def count(cls, comparison, constant, repeat, timeout):
      return {"count": {
                "comparison": comparison,
                "constant": constant,
                "count": count,
                "repeat": repeat,
                "timeout": timeout}
                }

  class Operation:
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    GT = "gt"
    GEQ = "geq"
    LT = "lt"
    LEQ = "leq"
    EQ = "eq"

