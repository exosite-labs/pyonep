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
  pass

class OnePlatformException(OneException):
  pass

class JsonRPCRequestException(OneException):
  pass

class JsonRPCResponseException(OneException):
  pass

class JsonStringException(OneException):
  pass
