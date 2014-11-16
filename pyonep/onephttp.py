'''onephttp.py
   HTTP Support library for One Platform
   Encapsulates an httplib connection so that various APIs
   do things like logging, https, and connection
   reuse in a consistent way.

   Usage:
       1. create an instance
       2. call request()
       3. call getresponse() to get a HTTPResponse object

   Copyright (c) 2014, Exosite LLC'''

import sys
try:
    import httplib
except:
    # python 3
    from http import client as httplib

class ConnectionFactory():
    '''Builds the correct kind of HTTPConnection object.'''
    @staticmethod
    def make_conn(hostport, https, timeout):
        '''Returns a HTTPConnection(-like) instance.

              hostport: the host and port to connect to, joined by a colon
              https: boolean indicating whether to use HTTPS
              timeout: number of seconds to wait for a response before HTTP timeout'''
        if https:
            cls = httplib.HTTPSConnection
        else:
            cls = httplib.HTTPConnection

        if sys.version_info < (2, 6):
            conn = cls(hostport)
        else:
            conn = cls(hostport, timeout=timeout)

        return conn

class OnePHTTPResponse:
    def __init__(self, exception=None, code=None, reason=None, body=None):
        self.exception = exception
        self.code = code
        self.reason = reason
        self.body = body


class OnePHTTP:
    def __init__(self,
                    host,
                    https=True,
                    httptimeout=5,
                    headers={},
                    reuseconnection=False,
                    log=None,
                    curldebug=False):
        self.host = host
        self.https = https
        self.httptimeout = httptimeout
        self.headers = headers
        self.reuseconnection = reuseconnection
        self.conn = None
        self.log = log
        self.curldebug = curldebug

    def request(self, method, path, body=None, headers={}, exception_fn=None):
        '''Wraps HTTPConnection.request. On exception it calls exception_fn
        with the exception object. If exception_fn is None, it re-raises the
        exception.'''
        allheaders = {}
        allheaders.update(self.headers)
        allheaders.update(headers)
        if self.conn is None or not self.reuseconnection:
            self.close()
            self.conn = ConnectionFactory.make_conn(
                self.host,
                self.https,
                self.httptimeout)
        try:
            if self.curldebug:
                # output request as a curl call
                def escape(s):
                    '''escape single quotes for bash'''
                    return s.replace("'", "'\\''")
                self.log.debug(
                    "curl {0}://{1}{2} -X {3} -m {4} {5} {6}".format(
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
            self.conn.request(method, path, body, allheaders)
        except Exception:
            self.close()
            ex = sys.exc_info()[1]
            if exception_fn is not None:
                exception_fn(ex)
            else:
                raise ex

    def getresponse(self, exception_fn=None):
        '''Wraps HTTPLib.getresponse. Exceptions handled as in request()'''
        try:
            response = self.conn.getresponse()
            if response.version == 10:
                version = 'HTTP/1.0'
            elif response.version == 11:
                version = 'HTTP/1.1'
            else:
                version = '%d' % response.version
            self.log.debug("%s %s %s\nHeaders: %s" % (
                version,
                response.status,
                response.reason,
                response.getheaders()))
            if response.getheader('Content-Type', '').endswith('charset=utf-8'):
                body = response.read().decode('utf_8')
            else:
                body = response.read()
            self.log.debug("Body: %s" % body)
            return body, response
        except Exception:
            self.close()
            ex = sys.exc_info()[1]
            if exception_fn is not None:
                exception_fn(ex)
            else:
                raise ex
        finally:
            if not self.reuseconnection:
                self.close()

    def close(self):
        '''Closes any open connection. This should only need to be called if
        reuseconnection is set to True. Once it's closed, the connection may be
        reopened by making another API called.'''
        if self.conn is not None:
            self.conn.close()
            self.conn = None
