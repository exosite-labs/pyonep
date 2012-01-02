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

import sys,httplib
from exceptions import *

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
#-------------------------------------------------------------------------------
  def __init__(self,host='m2.exosite.com',port='80',url='/api:v1/rpc/process',httptimeout=3):
    self.host        = host + ':' + port
    self.url         = url
    self.httptimeout = int(httptimeout)
    self._clientid   = None
    self._resourceid = None

#-------------------------------------------------------------------------------
  def __callJsonRPC(self, clientkey, callrequests):
    auth = self.__getAuth(clientkey)
    jsonreq = {"auth":auth,"calls":callrequests}
    if sys.version_info < (2 , 6):
     conn = httplib.HTTPConnection(self.host)
    else:
     conn = httplib.HTTPConnection(self.host, timeout=self.httptimeout)
    param = json.dumps(jsonreq)
    try:
      conn.request("POST", self.url, param, self.headers)
    except Exception:
      print sys.exc_info()[0]
      raise JsonRPCRequestException("Failed to make http request.")
    try:
      read = conn.getresponse().read()
    except Exception:
      print sys.exc_info()[0]
      raise JsonRPCResponseException("Failed to get response of request.")
    try:
      res = json.loads(read)
    except:
      raise OnePlatformException("Return invalid response value.")
    if isinstance(res,dict) and res.has_key('error'):
      raise OnePlatformException(res['error'])
    if isinstance(res,list) and len(res) > 0:
      if res[0].has_key('status'):
        if 'ok'  == res[0]['status']:
          if res[0].has_key('result'):
            return True,res[0]['result']
          return True,'ok'
        else:
          return False,res[0]['status']
      if res[0].has_key('error'):
        raise OnePlatformException(res[0]['error'])
    raise OneException("Unknown error")

#-------------------------------------------------------------------------------
  def __composeCall(self,method,argu):
    return [{"id":1,"procedure":method,"arguments":argu}]

#-------------------------------------------------------------------------------
  def __getAuth(self,clientkey):
    if None != self._clientid:
      return {"cik":clientkey,"client_id":self._clientid}
    elif None != self._resourceid:
      return {"cik":clientkey,"resource_id":self._resourceid}
    return {"cik":clientkey}

#-------------------------------------------------------------------------------
  def activate(self,clientkey,codetype,code):
    argu = [codetype, code]
    request = self.__composeCall("activate",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def comment(self, clientkey, rid, visibility, comment):
    argu = [rid, visibility, comment]
    request = self.__composeCall("comment",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def connect_as(self, clientid):
    self._clientid = clientid
    self._resourceid = None

#-------------------------------------------------------------------------------
  def connect_owner(self, resourceid):
    self._resourceid = resourceid
    self._clientid = None

#-------------------------------------------------------------------------------
  def create(self, clientkey, type, desc):
    argu = [type,desc]
    request = self.__composeCall("create",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def deactivate(self,clientkey,codetype,code):
    argu = [codetype, code]
    request = self.__composeCall("deactivate",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def drop(self, clientkey, rid):
    argu = [rid]
    request = self.__composeCall("drop",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def flush(self, clientkey, rid):
    argu = [rid]
    request = self.__composeCall("flush",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def info(self, clientkey, rid, options={}):
    argu = [rid,options]
    request = self.__composeCall("info",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def listing(self, clientkey, types, options):
    argu =[types,options]
    request = self.__composeCall("listing",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def lookup(self, clientkey, type, mapping):
    argu = [type,mapping]
    request = self.__composeCall("lookup",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def map(self, clientkey, rid, alias):
    argu = ["alias",rid,alias]
    request = self.__composeCall("map",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def read(self, clientkey, rid, options):
    argu = [rid,options]
    request = self.__composeCall("read",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def record(self, clientkey, rid, entries, options={}):
    argu = [rid, entries,options]
    request = self.__composeCall("record",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def revoke(self,clientkey,codetype,code):
    argu = [codetype, code]
    request = self.__composeCall("revoke",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def share(self, clientkey, rid, options={}):
    argu = [rid, options]
    request = self.__composeCall("share",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def unmap(self, clientkey, alias):
    argu = ["alias",alias]
    request = self.__composeCall("unmap",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def update(self, clientkey, rid, desc={}):
    argu = [rid,desc]
    request = self.__composeCall("update",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def write(self, clientkey, rid, value, options={}):
    argu = [rid,value,options]
    request = self.__composeCall("write",argu)
    return self.__callJsonRPC(clientkey,request)

#-------------------------------------------------------------------------------
  def writegroup(self, clientkey, entries, options={}):
    argu = [entries,options]
    request = self.__composeCall("write",argu)
    return self.__callJsonRPC(clientkey,request)
