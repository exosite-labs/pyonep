#==============================================================================
# provision.py
# This is API library for Exosite's One-Platform provision interface.
#==============================================================================
#
# Warning: pyonep version 0.8.0 introduces breaking change to the
#          provisioning interface. See README.md for details.
#
# Copyright (c) 2014, Exosite LLC
# All rights reserved.
#

import urllib
import logging
import sys
from pyonep import onephttp
from .exceptions import ProvisionException

if sys.version_info < (3, 0):
    urlencode = urllib.urlencode
else:
    urlencode = urllib.parse.urlencode

PROVISION_BASE = '/provision'
PROVISION_ACTIVATE = PROVISION_BASE + '/activate'
PROVISION_DOWNLOAD = PROVISION_BASE + '/download'
PROVISION_MANAGE = PROVISION_BASE + '/manage'
PROVISION_MANAGE_MODEL = PROVISION_MANAGE + '/model/'
PROVISION_MANAGE_CONTENT = PROVISION_MANAGE + '/content/'
PROVISION_REGISTER = PROVISION_BASE + '/register'

log = logging.getLogger(__name__)

# log errors stderr, don't log anything else
h = logging.StreamHandler()
h.setLevel(logging.ERROR)
log.addHandler(h)


class ProvisionResponse:
    def __init__(self, body, response):
        self.body = body
        self.response = response
        self.isok = self.response.status < 400

    def status(self):
        return self.response.status

    def reason(self):
        return self.response.reason

    def __repr__(self):
        return self.body

    def __str__(self):
        return "Status: {0}, Reason: {1}, Body: {2}".format(
            self.response.status,
            self.response.reason,
            self.body)


class Provision(object):
    def __init__(self,
                 host='m2.exosite.com',
                 port='80',
                 manage_by_cik=True,
                 verbose=False,
                 httptimeout=5,
                 https=False,
                 reuseconnection=False,
                 raise_api_exceptions=False,
                 curldebug=False):
        # backward compatibility
        protocol = 'http://'
        if host.startswith(protocol):
            host = host[len(protocol):]
        self._manage_by_cik = manage_by_cik
        self._verbose = verbose
        self._onephttp = onephttp.OnePHTTP(host + ':' + str(port),
                                           https=https,
                                           httptimeout=int(httptimeout),
                                           reuseconnection=reuseconnection,
                                           log=log,
                                           curldebug=curldebug)
        self._raise_api_exceptions = raise_api_exceptions

    def _filter_options(self, aliases=True, comments=True, historical=True):
        options = []
        if not aliases:
            options.append('noaliases')
        if not comments:
            options.append('nocomments')
        if not historical:
            options.append('nohistorical')
        return options

    def _request(self, path, key, data, method, key_is_cik, extra_headers={}):
        if method == 'GET':
            if len(data) > 0:
                url = path + '?' + data
            else:
                url = path
            body = None
        else:
            url = path
            body = data

        headers = {}
        if key_is_cik:
            headers['X-Exosite-CIK'] = key
        else:
            headers['X-Exosite-Token'] = key
        if method == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'
        headers['Accept'] = 'text/plain, text/csv, application/x-www-form-urlencoded'
        headers.update(extra_headers)

        self._onephttp.request(method,
                               url,
                               body,
                               headers)
        body, response = self._onephttp.getresponse()
        pr = ProvisionResponse(body, response)
        if self._raise_api_exceptions and not pr.isok:
            raise ProvisionException(pr)
        return pr

    def close(self):
        '''Closes any open connection. This should only need to be called if
        reuseconnection is set to True. Once it's closed, the connection may be
        reopened by making another API called.'''
        self.onephttp.close()

    def content_create(self, key, model, contentid, meta, protected=False):
        params = {'id': contentid, 'meta': meta}
        if protected is not False:
            params['protected'] = 'true'
        data = urlencode(params)
        path = PROVISION_MANAGE_CONTENT + model + '/'
        return self._request(path,
                             key, data, 'POST', self._manage_by_cik)

    def content_download(self, cik, vendor, model, contentid):
        data = urlencode({'vendor': vendor,
                                 'model': model,
                                 'id': contentid})
        headers = {"Accept": "*"}
        return self._request(PROVISION_DOWNLOAD,
                             cik, data, 'GET', True, headers)

    def content_info(self, key, model, contentid, vendor=None):
        if not vendor:  # if no vendor name, key should be the owner one
            path = PROVISION_MANAGE_CONTENT + model + '/' + contentid
            return self._request(path, key, '', 'GET', self._manage_by_cik)
        else:  # if provide vendor name, key can be the device one
            data = urlencode({'vendor': vendor,
                                     'model': model,
                                     'id': contentid,
                                     'info': 'true'})
            return self._request(PROVISION_DOWNLOAD,
                                 key, data, 'GET', self._manage_by_cik)

    def content_list(self, key, model):
        path = PROVISION_MANAGE_CONTENT + model + '/'
        return self._request(path, key, '', 'GET', self._manage_by_cik)

    def content_remove(self, key, model, contentid):
        path = PROVISION_MANAGE_CONTENT + model + '/' + contentid
        return self._request(path, key, '', 'DELETE', self._manage_by_cik)

    def content_upload(self, key, model, contentid, data, mimetype):
        headers = {"Content-Type": mimetype}
        path = PROVISION_MANAGE_CONTENT + model + '/' + contentid
        return self._request(path, key, data, 'POST', self._manage_by_cik, headers)

    def model_create(self, key, model, clonerid,
                     aliases=True, comments=True, historical=True):
        options = self._filter_options(aliases, comments, historical)
        data = urlencode({'model': model,
                                 'rid': clonerid,
                                 'options[]': options}, doseq=True)
        return self._request(PROVISION_MANAGE_MODEL,
                             key, data, 'POST', self._manage_by_cik)

    def model_info(self, key, model):
        return self._request(PROVISION_MANAGE_MODEL + model,
                             key, '', 'GET', self._manage_by_cik)

    def model_list(self, key):
        return self._request(PROVISION_MANAGE_MODEL,
                             key, '', 'GET', self._manage_by_cik)

    def model_remove(self, key, model):
        data = urlencode({'delete': 'true',
                                 'model': model,
                                 'confirm': 'true'})
        path = PROVISION_MANAGE_MODEL + model
        return self._request(path, key, data, 'DELETE', self._manage_by_cik)

    def model_update(self, key, model, clonerid,
                     aliases=True, comments=True, historical=True):
        options = self._filter_options(aliases, comments, historical)
        data = urlencode({'rid': clonerid,
                                 'options[]': options}, doseq=True)
        path = PROVISION_MANAGE_MODEL + model
        return self._request(path, key, data, 'PUT', self._manage_by_cik)

    def serialnumber_activate(self, model, serialnumber, vendor):
        data = urlencode({'vendor': vendor,
                                 'model': model,
                                 'sn': serialnumber})
        return self._request(PROVISION_ACTIVATE,
                             '', data, 'POST', self._manage_by_cik)

    def serialnumber_add(self, key, model, sn):
        data = urlencode({'add': 'true',
                                 'sn': sn})
        path = PROVISION_MANAGE_MODEL + model + '/'
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def serialnumber_add_batch(self, key, model, sns=[]):
        data = urlencode({'add': 'true',
                                 'sn[]': sns}, doseq=True)
        path = PROVISION_MANAGE_MODEL + model + '/'
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def serialnumber_disable(self, key, model, serialnumber):
        data = urlencode({'disable': 'true'})
        path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def serialnumber_enable(self, key, model, serialnumber, owner):
        data = urlencode({'enable': 'true', 'owner': owner})
        path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def serialnumber_info(self, key, model, serialnumber):
        path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
        return self._request(path, key, '', 'GET', self._manage_by_cik)

    def serialnumber_list(self, key, model, offset=0, limit=1000):
        data = urlencode({'offset': offset, 'limit': limit})
        path = PROVISION_MANAGE_MODEL + model + '/'
        return self._request(path, key, data, 'GET', self._manage_by_cik)

    def serialnumber_reenable(self, key, model, serialnumber):
        data = urlencode({'enable': 'true'})
        path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def serialnumber_remap(self, key, model, serialnumber, oldsn):
        data = urlencode({'enable': 'true', 'oldsn': oldsn})
        path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def serialnumber_remove(self, key, model, serialnumber):
        path = PROVISION_MANAGE_MODEL + model + '/' + serialnumber
        return self._request(path, key, '', 'DELETE', self._manage_by_cik)

    def serialnumber_remove_batch(self, key, model, sns):
        path = PROVISION_MANAGE_MODEL + model + '/'
        data = urlencode({'remove': 'true', 'sn[]': sns}, doseq=True)
        return self._request(path, key, data, 'POST', self._manage_by_cik)

    def vendor_register(self, key, vendor):
        data = urlencode({'vendor': vendor})
        return self._request(PROVISION_REGISTER,
                             key, data, 'POST', self._manage_by_cik)

    def vendor_show(self, key):
        return self._request(PROVISION_REGISTER, key, '', 'GET', False)

    def vendor_unregister(self, key, vendor):
        data = urlencode({'delete': 'true', 'vendor': vendor})
        return self._request(PROVISION_REGISTER,
                             key, data, 'POST', False)
