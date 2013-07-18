#==============================================================================
# provision.py
# This is API library for Exosite's One-Platform provision interface.
#==============================================================================
##
## Tested with python 2.6
##
## Copyright (c) 2011, Exosite LLC
## All rights reserved.
##
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2 smarttab

import urllib, urllib2, socket
from urllib2 import Request, urlopen, URLError, HTTPError
# timeout in seconds
timeout = 5
socket.setdefaulttimeout(timeout)
PROVISION_BASE = '/provision'
PROVISION_ACTIVATE         = PROVISION_BASE +  '/activate'
PROVISION_DOWNLOAD         = PROVISION_BASE + '/download'
PROVISION_MANAGE           = PROVISION_BASE + '/manage'
PROVISION_MANAGE_MODEL     = PROVISION_MANAGE + '/model/'
PROVISION_MANAGE_CONTENT   = PROVISION_MANAGE + '/content/'
PROVISION_REGISTER         = PROVISION_BASE + '/register'

class Provision(object):
  def __init__(self, host='http://m2.exosite.com'):
    self._host = host

  def _filter_options(self, aliases=True, comments= True, historical=True):
    options = []
    if not aliases: options.append('noaliases')
    if not comments: options.append('nocomments')
    if not historical: options.append('nohistorical')
    return options

  def _request(self, path, cik, data, method, extra_headers={}):
    if method == "GET":
      url = self._host + path + '?' + data
      req = urllib2.Request(url)
    else:
      url = self._host + path
      req = urllib2.Request(url, data)
    req.add_header('X-Exosite-CIK',cik)
    req.add_header('Accept',
                   'text/plain, text/csv, application/x-www-form-urlencoded')
    for name in extra_headers.keys():
      req.add_header(name, extra_headers[name])
    req.get_method = lambda : method
    try:
      resp = urllib2.urlopen(req)
      return resp.read()
    except HTTPError, e:
      print 'Http error code: ' + str(e.code)
    except URLError, e:
      print 'Failed to reach server! Reason: ' + str(e.reason)
    return None

  def content_create(self, cik, model, contentid, description):
    data = urllib.urlencode({'id':contentid, 'description':description})
    path = PROVISION_MANAGE_CONTENT + model + '/'
    return self._request(path, cik, data, 'POST') != None

  def content_download(self, cik, vendor, model, contentid):
    data = urllib.urlencode({'vendor':vendor, 'model': model, 'id':contentid})
    headers = {"Accept":"*"}
    return self._request(PROVISION_DOWNLOAD, cik, data, 'GET', headers)

  def content_info(self, cik, model, contentid):
    path = PROVISION_MANAGE_CONTENT + model + '/' + contentid
    return self._request(path, cik, '', 'GET')

  def content_list(self, cik, model):
    path = PROVISION_MANAGE_CONTENT + model + '/'
    return self._request(path, cik, '', 'GET')

  def content_remove(self, cik, model, contentid):
    path = PROVISION_MANAGE_CONTENT + model + '/' + contentid
    return self._request(path, cik, '', 'DELETE') != None

  def content_upload(self, cik, model, contentid, data, mimetype):
    headers = {"Content-Type":mimetype}
    path = PROVISION_MANAGE_CONTENT + model + '/' + contentid
    return self._request(path, cik, data  , 'POST', headers) != None

  def model_create(self, cik, model ,clonerid,
                   aliases=True, comments=True, historical=True):
    options = self._filter_options(aliases, comments, historical)
    data = urllib.urlencode({'model': model, 'rid': clonerid,
                            'options[]':options}, doseq=True)
    return self._request(PROVISION_MANAGE_MODEL, cik, data, 'POST') != None

  def model_info(self, cik, model):
    return self._request(PROVISION_MANAGE_MODEL + model, cik, '', 'GET')

  def model_list(self, cik):
    return self._request(PROVISION_MANAGE_MODEL, cik, '', 'GET')

  def model_remove(self, cik, model):
    data = urllib.urlencode({ 'delete':'true', 'model':model, 'confirm':'true'})
    path = PROVISION_MANAGE_MODEL + model
    return self._request(path, cik, data, 'DELETE') != None

  def model_update(self, cik, model, clonerid,
                   aliases=True, comments= True, historical=True):
    options = self._filter_options(aliases, comments, historical)
    data = urllib.urlencode({'rid':clonerid, 'options[]':options}, doseq=True)
    path = PROVISION_MANAGE_MODEL + model
    return self._request(path, cik, data, 'PUT') != None

  def serialnumber_activate(self, model, serialnumber, vendor):
    data = urllib.urlencode({'vendor':vendor, 'model':model, 'sn':serialnumber})
    return self._request(PROVISION_ACTIVATE, '', data, 'POST')

  def serialnumber_add(self, cik, model, sn):
    data = urllib.urlencode({'add':'true', 'sn':sn})
    path = PROVISION_MANAGE_MODEL + model + '/'
    return self._request(path, cik, data, 'POST') != None

  def serialnumber_add_batch(self, cik, model, sns=[]):
    data = urllib.urlencode({'add':'true', 'sn[]':sns}, doseq=True)
    path = PROVISION_MANAGE_MODEL + model + '/'
    return self._request(path, cik, data, 'POST') != None

  def serialnumber_disable(self, cik, model, serialnumber):
    data = urllib.urlencode({'disable':'true'})
    path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
    return self._request(path, cik, data, 'POST')

  def serialnumber_enable(self, cik, model, serialnumber, owner):
    data = urllib.urlencode({'enable':'true', 'owner':owner})
    path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
    return self._request(path, cik, data, 'POST')

  def serialnumber_info(self, cik, model, serialnumber):
    path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
    return self._request(path, cik, '', 'GET')

  def serialnumber_list(self, cik, model, offset=0, limit=1000):
    data = urllib.urlencode({'offset':offset, 'limit':limit})
    path = PROVISION_MANAGE_MODEL + model + '/'
    return self._request(path, cik, data, 'GET')

  def serialnumber_reenable(self, cik, model, serialnumber):
    data = urllib.urlencode({'enable':'true'})
    path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
    return self._request(path, cik, data, 'POST')

  def serialnumber_remap(self, cik, model, serialnumber, oldsn):
    data = urllib.urlencode({'enable':'true', 'oldsn':oldsn})
    path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
    return self._request(path, cik, data, 'POST') != None

  def serialnumber_remove(self, cik, model, serialnumber):
    path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
    return self._request(path, cik, '', 'DELETE') != None

  def serialnumber_remove_batch(self, cik, model, sns):
    path = PROVISION_MANAGE_MODEL + model + '/'
    data = urllib.urlencode({'remove':'true', 'sn[]':sns}, doseq=True)
    return self._request(path, cik, data, 'POST') != None

  def vendor_register(self, cik, vendor):
    data = urllib.urlencode({'vendor':vendor})
    return self._request(PROVISION_REGISTER, cik, data, 'POST') != None

  def vendor_unregister(self, cik, vendor):
    data = urllib.urlencode({'delete':'true','vendor':vendor})
    return self._request(PROVISION_REGISTER, cik, data, 'POST') != None
