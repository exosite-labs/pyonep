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
    '''Encapsulates a list of deferred requests for each auth/CIK. Once the requests
        are ready to be sent, get_method_args_pairs() returns a list of the
        method name and arguments for each request.'''
    def __init__(self):
        self._requests = {}

    def _authstr(self, auth):
        '''Convert auth to str so that it can be hashed'''
        if type(auth) is dict:
            return '{' + ','.join(["{0}:{1}".format(k, auth[k]) for k in sorted(auth.keys())]) + '}'
        else:
            return auth

    def add(self, auth, method, args):
        '''Append a deferred request for a particular auth/CIK.'''
        self._requests.setdefault(self._authstr(auth), []).append((method, args))

    def reset(self, auth):
        self._requests.pop(self._authstr(auth))

    def has_requests(self, auth):
        '''Returns True if there are any deferred requests for
        auth/CIK, False otherwise.'''
        authstr = self._authstr(auth)
        return (authstr in self._requests
                and len(self._requests[authstr]) > 0)

    def get_method_args_pairs(self, auth):
        '''Returns a list of method/arguments pairs corresponding to deferred
        requests for this auth/CIK'''
        return self._requests[self._authstr(auth)]


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
                 logrequests=False,
                 curldebug=False):
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
                                          log=log,
                                          curldebug=curldebug)

    def close(self):
        '''Closes any open connection. This should only need to be called if
        reuseconnection is set to True. Once it's closed, the connection may be
        reopened by making another API called.'''
        self.onephttp.close()

    _loggedrequests = []

    def loggedrequests(self):
        '''Returns a list of request bodies made by this instance of OnepV1'''
        return self._loggedrequests

    def _callJsonRPC(self, auth, callrequests, returnreq=False):
        '''Calls the Exosite One Platform RPC API.
            If returnreq is False, result is a tuple with this structure:
                (success (boolean), response)

            If returnreq is True, result is a list of tuples with
            this structure:
                (request, success, response)
                '''
        # get full auth (auth could be a CIK str)
        auth = self._getAuth(auth)
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

    def _getAuth(self, auth):
        '''Create the authorization/identification portion of a request.'''
        if type(auth) is dict:
            return auth
        else:
            # auth is string
            if None != self._clientid:
                return {"cik": auth, "client_id": self._clientid}
            elif None != self._resourceid:
                return {"cik": auth, "resource_id": self._resourceid}
            return {"cik": auth}

    def _composeCalls(self, method_args_pairs):
        calls = []
        i = random.randint(1, 99)
        for method, args in method_args_pairs:
            calls.append({'id': i,
                          'procedure': method,
                          'arguments': args})
            i += 1
        return calls

    def _call(self, method, auth, arg, defer):
        if defer:
            self.deferred.add(auth, method, arg)
            return True
        else:
            calls = self._composeCalls([(method, arg)])
            return self._callJsonRPC(auth, calls)

    def has_deferred(self, auth):
        return self.deferred.has_requests(auth)

    def send_deferred(self, auth):
        '''Send all deferred requests for a particular CIK/auth.'''
        if self.deferred.has_requests(auth):
            calls = self._composeCalls(
                self.deferred.get_method_args_pairs(auth))
            try:
                r = self._callJsonRPC(auth, calls, returnreq=True)
            finally:
                # remove deferred calls
                self.deferred.reset(auth)
            return r
        raise JsonRPCRequestException('No deferred requests to send.')

    def connect_as(self, clientid):
        self._clientid = clientid
        self._resourceid = None

    def connect_owner(self, resourceid):
        self._resourceid = resourceid
        self._clientid = None

    # API methods
    def activate(self, auth, codetype, code, defer=False):
        return self._call('activate', auth, [codetype, code], defer)

    def create(self, auth, type, desc, defer=False):
        return self._call('create', auth, [type, desc], defer)

    def deactivate(self, auth, codetype, code, defer=False):
        return self._call('deactivate', auth, [codetype, code], defer)

    def drop(self, auth, rid, defer=False):
        return self._call('drop', auth, [rid], defer)

    def flush(self, auth, rid, options=None, defer=False):
        args = [rid]
        if options is not None:
            args.append(options)
        return self._call('flush', auth, args, defer)

    def info(self, auth, rid, options={}, defer=False):
        return self._call('info', auth,  [rid, options], defer)

    def listing(self, auth, rid, types, options, defer=False):
        if type(rid) is list:
            raise Exception('listing without RID or options is no longer supported http://docs.exosite.com/rpc/#listing')
        return self._call('listing', auth, [rid, types, options], defer)

    def lookup(self, auth, type, mapping, defer=False):
        return self._call('lookup', auth, [type, mapping], defer)

    def map(self, auth, rid, alias, defer=False):
        return self._call('map', auth, ['alias', rid, alias], defer)

    def read(self, auth, rid, options, defer=False):
        return self._call('read', auth, [rid, options], defer)

    def record(self, auth, rid, entries, options={}, defer=False):
        return self._call('record', auth, [rid, entries, options], defer)

    def recordbatch(self, auth, rid, entries, defer=False):
        return self._call('recordbatch', auth, [rid, entries], defer)

    def revoke(self, auth, codetype, code, defer=False):
        return self._call('revoke', auth, [codetype, code], defer)

    def share(self, auth, rid, options={}, defer=False):
        return self._call('share', auth, [rid, options], defer)

    def tag(self, auth, rid, action, tag, defer=False):
        return self._call('tag', auth, [rid, action, tag], defer)

    def unmap(self, auth, alias, defer=False):
        return self._call('unmap', auth, ['alias', alias], defer)

    def update(self, auth, rid, desc={}, defer=False):
        return self._call('update', auth, [rid, desc], defer)

    def usage(self, auth, rid, metric, starttime, endtime, defer=False):
        return self._call('usage', auth,
                          [rid, metric, starttime, endtime], defer)

    def write(self, auth, rid, value, options={}, defer=False):
        return self._call('write', auth, [rid, value, options], defer)

    def writegroup(self, auth, entries, defer=False):
        return self._call('writegroup', auth, [entries], defer)
