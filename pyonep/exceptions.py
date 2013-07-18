#==============================================================================
# exceptions.py
# exception handler for Exosite HTTP JSON RPC API library (man, alphabet soup)
#==============================================================================
##
## Tested with python 2.6
##
## Copyright (c) 2010, Exosite LLC
## All rights reserved.
##
# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2 smarttab

class OneException(Exception):
  def __init__(self, message):
    self.message = message

  def _get_message(self):
    return self._message

  def _set_message(self, message):
    self._message = message

  message = property(_get_message, _set_message)

class OnePlatformException(OneException):
  pass

class JsonRPCRequestException(OneException):
  pass

class JsonRPCResponseException(OneException):
  pass

class JsonStringException(OneException):
  pass
