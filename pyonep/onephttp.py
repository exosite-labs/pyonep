"""onephttp.py
   HTTP Support library for One Platform
   Encapsulates an httplib connection so that various APIs
   do things like logging, https, and connection
   reuse in a consistent way.

   Usage:
       1. create an instance
       2. call request()
       3. call getresponse() to get a HTTPResponse object

   Copyright (c) 2016, Exosite LLC"""
# pylint: disable = W0312

import sys

from requests import Session, Request


class OneP_Request:
    def __init__(self,
                 host,
                 https=True,
                 httptimeout=15,
                 headers={},
                 reuseconnection=False,
                 log=None,
                 curldebug=False):
        self.host = ('https://' + host) if https else ('http://' + host)
        self.https = https
        self.httptimeout = httptimeout
        self.headers = headers
        self.reuseconnection = reuseconnection
        self.session = Session()
        self.session.headers.update(self.headers)
        self.log = log
        self.curldebug = curldebug

    def request(self,
                method,
                path,
                body=None,
                headers={},
                exception_fn=None,
                notimeout=False,
                verify=True):
        """Wraps HTTPConnection.request. On exception it calls exception_fn
        with the exception object. If exception_fn is None, it re-raises the
        exception. If notimeout is True, create a new connection (regardless of
        self.reuseconnection setting) that uses the global default timeout for
        sockets (usually None)."""
        # This needs to be done first because self.session may be None
        if not self.reuseconnection or notimeout:
            self.close()
            self.session = Session()

        allheaders = headers
        allheaders.update(self.session.headers)

        try:
            if self.curldebug:
                # output request as a curl call
                def escape(s):
                    """escape single quotes for bash"""
                    return s.replace("'", "'\\''")

                self.log.debug(
                    "curl '{1}{2}' -X {3} -m {4} {5} {6}".format(
                        'https' if self.https else 'http',
                        self.host,
                        path,
                        method,
                        self.httptimeout,
                        ' '.join(['-H \'{0}: {1}\''.format(escape(h), escape(allheaders[h]))
                                  for h in allheaders]),
                        '' if body is None else '-d \'' + escape(body) + '\''))
            else:
                self.log.debug("%s %s\nHost: %s\nHeaders: %s" % (
                    method,
                    path,
                    self.host,
                    allheaders))
                if body is not None:
                    self.log.debug("Body: %s" % body)
            URI = self.host + path
            prepped = self.session.prepare_request(
                Request(method, URI, data=body, headers=headers)
            )

            response = self.session.send(
                prepped,
                verify=verify,
                timeout=None if notimeout else self.httptimeout
            )
            return response.text, response

        except Exception:
            self.close()
            ex = sys.exc_info()[1]
            if exception_fn is not None:
                exception_fn(ex)
            else:
                raise ex

    def close(self):
        """Closes any open connection. This should only need to be called if
        reuseconnection is set to True. Once it's closed, the connection may be
        reopened by making another API called."""
        if self.session is not None:
            self.session.close()
            self.session = None
