# ==============================================================================
# onep.py
# Main API library class for Exosite's One Platform as exposed over HTTP JSON
# RPC
# ==============================================================================
#
# Copyright (c) 2016, Exosite LLC
# All rights reserved.
#
import sys
import logging

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


class FORMATS:
    STRING = 'string'
    FLOAT = 'float'
    INTEGER = 'integer'


class DeferredRequests():
    """Encapsulates a list of deferred requests for each auth/CIK. Once the requests
        are ready to be sent, get_method_args_pairs() returns a list of the
        method name and arguments for each request and get_notimeout() returns whether
        the client should time out."""

    def __init__(self):
        self._requests = {}
        self._notimeouts = {}

    def _authstr(self, auth):
        """Convert auth to str so that it can be hashed"""
        if type(auth) is dict:
            return '{' + ','.join(["{0}:{1}".format(k, auth[k]) for k in sorted(auth.keys())]) + '}'
        return auth

    def add(self, auth, method, args, notimeout=False):
        """Append a deferred request for a particular auth/CIK."""
        authstr = self._authstr(auth)
        self._requests.setdefault(authstr, []).append((method, args))
        self._notimeouts.setdefault(authstr, False)
        if notimeout:
            self._notimeouts[authstr] = notimeout

    def reset(self, auth):
        self._requests.pop(self._authstr(auth))

    def has_requests(self, auth):
        """Returns True if there are any deferred requests for
        auth/CIK, False otherwise."""
        authstr = self._authstr(auth)
        return (authstr in self._requests
                and len(self._requests[authstr]) > 0)

    def get_method_args_pairs(self, auth):
        """Returns a list of method/arguments pairs corresponding to deferred
        calls for this auth/CIK"""
        return self._requests[self._authstr(auth)]

    def get_notimeout(self, auth):
        """Returns a boolean representing whether timeout setting should be used
        for deferred calls for this auth/CIK"""
        return self._notimeouts[self._authstr(auth)]


class OnepV1():
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    def __init__(self,
                 host='m2.exosite.com',
                 port='443',
                 url='/onep:v1/rpc/process',
                 https=True,
                 httptimeout=10,
                 agent=None,
                 reuseconnection=False,
                 logrequests=False,
                 curldebug=False,
                 startid=0):
        self.url = url
        self._clientid = None
        self._resourceid = None
        self.deferred = DeferredRequests()
        if agent is not None:
            self.headers['User-Agent'] = agent
        self.logrequests = logrequests
        # starting ID for RPC calls
        self.startid = startid
        self.onephttp = onephttp.OneP_Request(host + ':' + str(port),
                                              https=https,
                                              httptimeout=int(httptimeout),
                                              headers=self.headers,
                                              reuseconnection=reuseconnection,
                                              log=log,
                                              curldebug=curldebug)

    def close(self):
        """Closes any open connection. This should only need to be called if
        reuseconnection is set to True. Once it's closed, the connection may be
        reopened by making another API called."""
        self.onephttp.close()

    _loggedrequests = []

    def loggedrequests(self):
        """Returns a list of request bodies made by this instance of OnepV1"""
        return self._loggedrequests

    def _callJsonRPC(self, auth, callrequests, returnreq=False, notimeout=False):
        """Calls the Exosite One Platform RPC API.
            If returnreq is False, result is a tuple with this structure:
                (success (boolean), response)

            If returnreq is True, result is a list of tuples with
            this structure:
                (request, success, response)
            notimeout, if true, ignores reuseconnection setting, creating
            a new connection with no timeout.
                """
        # get full auth (auth could be a CIK str)
        auth = self._getAuth(auth)
        jsonreq = {"auth": auth, "calls": callrequests}
        if self.logrequests:
            self._loggedrequests.append(jsonreq)
        body = json.dumps(jsonreq)

        def handle_request_exception(exception):
            raise JsonRPCRequestException(
                "Failed to make http request: %s" % str(exception))

        body, response = self.onephttp.request('POST',
                                               self.url,
                                               body,
                                               self.headers,
                                               exception_fn=handle_request_exception,
                                               notimeout=notimeout)

        def handle_response_exception(exception):

            raise JsonRPCResponseException(
                "Failed to get response for request: %s %s" % (type(exception), str(exception)))

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
        """Create the authorization/identification portion of a request."""
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
        for method, args in method_args_pairs:
            calls.append({'id': self.startid,
                          'procedure': method,
                          'arguments': args})
            self.startid += 1
        return calls

    def _call(self, method, auth, arg, defer, notimeout=False):
        """Calls the Exosite One Platform RPC API.

           If `defer` is False, result is a tuple with this structure:

                (success (boolean), response)

           Otherwise, the result is just True.

           notimeout, if True, ignores the reuseconnection setting, creating
           a new connection with no timeout.
        """
        if defer:
            self.deferred.add(auth, method, arg, notimeout=notimeout)
            return True
        else:
            calls = self._composeCalls([(method, arg)])
            return self._callJsonRPC(auth, calls, notimeout=notimeout)

    def has_deferred(self, auth):
        return self.deferred.has_requests(auth)

    def send_deferred(self, auth):
        """Send all deferred requests for a particular CIK/auth."""
        if self.deferred.has_requests(auth):
            method_arg_pairs = self.deferred.get_method_args_pairs(auth)
            calls = self._composeCalls(method_arg_pairs)
            # should this call be made with no timeout? (e.g. is there a
            # wait())
            notimeout = self.deferred.get_notimeout(auth)
            try:
                r = self._callJsonRPC(auth, calls, returnreq=True, notimeout=notimeout)
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
        """ Given an activation code, activate an entity for the client specified in <ResourceID>.

        Args:
            auth: <cik>
            codetype: Type of code being activated.
            code: Code to activate.
        """

        return self._call('activate', auth, [codetype, code], defer)

    def create(self, auth, type, desc, defer=False):
        """ Create something in Exosite.

        Args:
            auth: <cik>
            type: What thing to create.
            desc: Information about thing.
        """
        return self._call('create', auth, [type, desc], defer)

    def createDataport(self, auth, desc, defer=False):
        """Create a dataport resource.
           "format" and "retention" are required
            {
                "format": "float" | "integer" | "string",
                "meta": string = "",
                "name": string = "",
                "preprocess": list = [],
                "public": boolean = false,
                "retention": {
                    "count": number | "infinity",
                    "duration": number | "infinity"
                },
                "subscribe": <ResourceID> |  null = null
            }
        """
        return self._call('create', auth, ['dataport', desc], defer)

    def deactivate(self, auth, codetype, code, defer=False):
        return self._call('deactivate', auth, [codetype, code], defer)

    def drop(self, auth, resource, defer=False):
        """ Deletes the specified resource.

        Args:
            auth: <cik>
            resource: <ResourceID>
        """
        return self._call('drop', auth, [resource], defer)

    def flush(self, auth, resource, options=None, defer=False):
        """ Empties the specified resource of data per specified constraints.

        Args:
            auth: <cik>
            resource: resource to empty.
            options: Time limits.
        """
        args = [resource]
        if options is not None:
            args.append(options)
        return self._call('flush', auth, args, defer)

    def grant(self, auth, resource, permissions, ttl=None, defer=False):
        """ Grant resources with specific permissions and return a token.

        Args:
            auth: <cik>
            resource: Alias or ID of resource.
            permissions: permissions of resources.
            ttl: Time To Live.
        """
        args = [resource, permissions]
        if ttl is not None:
            args.append({"ttl": ttl})
        return self._call('grant', auth, args, defer)

    def info(self, auth, resource, options={}, defer=False):
        """ Request creation and usage information of specified resource according to the specified
        options.

        Args:
            auth: <cik>
            resource: Alias or ID of resource
            options: Options to define what info you would like returned.
        """
        return self._call('info', auth,  [resource, options], defer)

    def listing(self, auth, types, options=None, resource=None, defer=False):
        """This provides backward compatibility with two
           previous variants of listing. To use the non-deprecated
           API, pass both options and resource."""
        if options is None:
            # This variant is deprecated
            return self._call('listing', auth, [types], defer)
        else:
            if resource is None:
                # This variant is deprecated, too
                return self._call('listing',
                                  auth,
                                  [types, options],
                                  defer)
            else:
                # pass resource to use the non-deprecated variant
                return self._call('listing',
                                  auth,
                                  [resource, types, options],
                                  defer)

    def lookup(self, auth, type, mapping, defer=False):
        """ Look up a Resource ID by alias, owned Resource ID, or share activation code under the
        client specified in <ClientID>.

        Args:
            auth: <cik>
            type: Type of resource to lookup (alias | owner | shared)
            mapping: Based on resource type defined above.
        """
        return self._call('lookup', auth, [type, mapping], defer)

    def map(self, auth, resource, alias, defer=False):
        """ Creates an alias for a resource.

        Args:
            auth: <cik>
            resource: <ResourceID>
            alias: alias to create (map)
        """
        return self._call('map', auth, ['alias', resource, alias], defer)

    def move(self, auth, resource, destinationresource, options={"aliases": True}, defer=False):
        """ Moves a resource from one parent client to another.

        Args:
            auth: <cik>
            resource: Identifed resource to be moved.
            destinationresource: resource of client resource is being moved to.
        """
        return self._call('move', auth, [resource, destinationresource, options], defer)

    def read(self, auth, resource, options, defer=False):
        """ Read value(s) from a dataport.

        Calls a function that builds a request to read the dataport specified by an alias or rid
        and returns timeseries data as defined by the options.

        Args:
            auth: Takes the device cik
            resource: Takes the dataport alias or rid.
            options: Takes a list of options for what to return.
        """
        return self._call('read', auth, [resource, options], defer)

    def record(self, auth, resource, entries, options={}, defer=False):
        """ Records a list of historical entries to the resource specified.

        Note: This API is depricated, use recordbatch instead.

        Calls a function that bulids a request that writes a list of historical entries to the
        specified resource.

        Args:
            auth: Takes the device cik
            resource: Takes the dataport alias or rid.
            entries: A list of entries to write to the resource.
            options: Currently unused.
        """
        return self._call('record', auth, [resource, entries, options], defer)

    def recordbatch(self, auth, resource, entries, defer=False):
        """ Records a list of historical entries to the resource specified.

        Calls a function that bulids a request that writes a list of historical entries to the
        specified resource.

        Args:
            auth: Takes the device cik
            resource: Takes the dataport alias or rid.
            entries: A list of entries to write to the resource.
        """
        return self._call('recordbatch', auth, [resource, entries], defer)

    def revoke(self, auth, codetype, code, defer=False):
        """ Given an activation code, the associated entity is revoked after which the activation
        code can no longer be used.

        Args:
            auth: Takes the owner's cik
            codetype: The type of code to revoke (client | share)
            code: Code specified by <codetype> (cik | share-activation-code)
        """
        return self._call('revoke', auth, [codetype, code], defer)

    def share(self, auth, resource, options={}, defer=False):
        """ Generates a share code for the given resource.

        Args:
            auth: <cik>
            resource: The identifier of the resource.
            options: Dictonary of options.
        """
        return self._call('share', auth, [resource, options], defer)

    def tag(self, auth, resource, action, tag, defer=False):
        return self._call('tag', auth, [resource, action, tag], defer)

    def unmap(self, auth, alias, defer=False):
        return self._call('unmap', auth, ['alias', alias], defer)

    def update(self, auth, resource, desc={}, defer=False):
        """ Updates the description of the resource.

        Args:
            auth: <cik> for authentication
            resource: Resource to be updated
            desc: A Dictionary containing the update for the resource.
        """
        return self._call('update', auth, [resource, desc], defer)

    def usage(self, auth, resource, metric, starttime, endtime, defer=False):
        """ Returns metric usage for client and its subhierarchy.

        Args:
            auth: <cik> for authentication
            resource: ResourceID
            metrics: Metric to measure (as string), it may be an entity or consumable.
            starttime: Start time of window to measure useage (format is ___).
            endtime: End time of window to measure useage (format is ___).
        """
        return self._call('usage', auth,
                          [resource, metric, starttime, endtime], defer)

    def wait(self, auth, resource, options, defer=False):
        """ This is a HTTP Long Polling API which allows a user to wait on specific resources to be
        updated.

        Args:
            auth: <cik> for authentication
            resource: <ResourceID> to specify what resource to wait on.
            options: Options for the wait including a timeout (in ms), (max 5min) and start time
            (null acts as when request is recieved)
        """
        # let the server control the timeout
        return self._call('wait', auth, [resource, options], defer, notimeout=True)

    def write(self, auth, resource, value, options={}, defer=False):
        """ Writes a single value to the resource specified.

        Args:
            auth: cik for authentication.
            resource: resource to write to.
            value: value to write
            options: options.
        """
        return self._call('write', auth, [resource, value, options], defer)

    def writegroup(self, auth, entries, defer=False):
        """ Writes the given values for the respective resources in the list, all writes have same
        timestamp.

        Args:
            auth: cik for authentication.
            entries: List of key, value lists. eg. [[key, value], [k,v],,,]
        """
        return self._call('writegroup', auth, [entries], defer)
