#==============================================================================
# onep.py
# Main API library class for Exosite's Data Platform as exposed over HTTP JSON
# RPC
#==============================================================================
#
# Copyright (c) 2014, Exosite LLC
# All rights reserved.
#
import sys
import logging
import random

from pyonep import onephttp
from .exceptions import OneException, OnePlatformException
from .exceptions import JsonRPCRequestException, JsonRPCResponseException

log = logging.getLogger(__name__)

# log errors stderr, don't log anything else
h = logging.StreamHandler()
h.setLevel(logging.ERROR)
log.addHandler(h)

try:
    if sys.version_info < (2, 6):
        json_module = 'python-simplejson'
        import simplejson as json
    else:
        json_module = 'python-json'
        import json
except ImportError:
    log.critical("The package '%s' is required." % json_module)
    sys.exit(1)


class DeferredRequests():
    '''Encapsulates a list of deferred requests for each CIK. Once the requests
        are ready to be sent, get_method_args_pairs() returns a list of the
        method name and arguments for each request.'''
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
        return (cik in self._requests
                and len(self._requests[cik]) > 0)

    def get_method_args_pairs(self, cik):
        '''Returns a list of method/arguments pairs corresponding to deferred
        requests for this CIK'''
        return self._requests[cik]


class OnepV1():
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    def __init__(self,
                 host='m2.exosite.com',
                 port='80',
                 url='/onep:v1/rpc/process',
                 https=False,
                 httptimeout=10,
                 agent=None,
                 reuseconnection=False,
                 logrequests=False):
        self.url = url
        self._clientid = None
        self._resourceid = None
        self.deferred = DeferredRequests()
        if agent is not None:
            self.headers['User-Agent'] = agent
        self.logrequests = logrequests
        self.onephttp = onephttp.OnePHTTP(host + ':' + str(port),
                                          https=https,
                                          httptimeout=int(httptimeout),
                                          headers=self.headers,
                                          reuseconnection=reuseconnection,
                                          log=log)

    def close(self):
        '''Closes any open connection. This should only need to be called if
        reuseconnection is set to True. Once it's closed, the connection may be
        reopened by making another API called.'''
        self.onephttp.close()

    _loggedrequests = []

    def loggedrequests(self):
        '''Returns a list of request bodies made by this instance of OnepV1'''
        return self._loggedrequests

    def _callJsonRPC(self, cik, callrequests, returnreq=False):
        '''Calls the Exosite One Platform RPC API.
            If returnreq is False, result is a tuple with this structure:
                (success (boolean), response)

            If returnreq is True, result is a list of tuples with
            this structure:
                (request, success, response)
                '''
        auth = self._getAuth(cik)
        jsonreq = {"auth": auth, "calls": callrequests}
        if self.logrequests:
            self._loggedrequests.append(jsonreq)
        body = json.dumps(jsonreq)

        def handle_request_exception(exception):
            raise JsonRPCRequestException(
                "Failed to make http request: %s" % str(exception))

        self.onephttp.request('POST',
                              self.url,
                              body,
                              self.headers,
                              exception_fn=handle_request_exception)

        def handle_response_exception(exception):
            raise JsonRPCResponseException(
                "Failed to get response for request: %s" % str(exception))

        body, response = self.onephttp.getresponse(
            exception_fn=handle_response_exception)

        try:
            res = json.loads(body)
        except:
            ex = sys.exc_info()[1]
            raise OnePlatformException(
                "Exception while parsing JSON response: %s\n%s" % (body, ex))
        if isinstance(res, dict) and 'error' in res:
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
                if 'status' in r:
                    if 'ok' == r['status']:
                        if 'result' in r:
                            ret.append((request, True, r['result']))
                        else:
                            ret.append((request, True, 'ok'))
                    else:
                        ret.append((request, False, r['status']))
                elif 'error' in r:
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
        i = random.randint(1, 99)
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
            calls = self._composeCalls(
                self.deferred.get_method_args_pairs(cik))
            try:
                r = self._callJsonRPC(cik, calls, returnreq=True)
            finally:
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

    def create(self, cik, type, desc, defer=False):
        return self._call('create', cik, [type, desc], defer)

    def deactivate(self, cik, codetype, code, defer=False):
        return self._call('deactivate', cik, [codetype, code], defer)

    def drop(self, cik, rid, defer=False):
        return self._call('drop', cik, [rid], defer)

    def flush(self, cik, rid, options=None, defer=False):
        args = [rid]
        if options is not None:
            args.append(options)
        return self._call('flush', cik, args, defer)

    def info(self, cik, rid, options={}, defer=False):
        return self._call('info', cik,  [rid, options], defer)

    def listing(self, cik, types, options=None, defer=False):
        if options is None:
            # This variant is deprecated
            return self._call('listing', cik, [types], defer)
        else:
            return self._call('listing', cik, [types, options], defer)

    def lookup(self, cik, type, mapping, defer=False):
        return self._call('lookup', cik, [type, mapping], defer)

    def map(self, cik, rid, alias, defer=False):
        return self._call('map', cik, ['alias', rid, alias], defer)

    def read(self, cik, rid, options, defer=False):
        return self._call('read', cik, [rid, options], defer)

    def record(self, cik, rid, entries, options={}, defer=False):
        return self._call('record', cik, [rid, entries, options], defer)

    def recordbatch(self, cik, rid, entries, defer=False):
        return self._call('recordbatch', cik, [rid, entries], defer)

    def revoke(self, cik, codetype, code, defer=False):
        return self._call('revoke', cik, [codetype, code], defer)

    def share(self, cik, rid, options={}, defer=False):
        return self._call('share', cik, [rid, options], defer)

    def tag(self, cik, rid, action, tag, defer=False):
        return self._call('tag', cik, [rid, action, tag], defer)

    def unmap(self, cik, alias, defer=False):
        return self._call('unmap', cik, ['alias', alias], defer)

    def update(self, cik, rid, desc={}, defer=False):
        return self._call('update', cik, [rid, desc], defer)

    def usage(self, cik, rid, metric, starttime, endtime, defer=False):
        return self._call('usage', cik,
                          [rid, metric, starttime, endtime], defer)

    def write(self, cik, rid, value, options={}, defer=False):
        return self._call('write', cik, [rid, value, options], defer)

    def writegroup(self, cik, entries, defer=False):
        return self._call('writegroup', cik, [entries], defer)
