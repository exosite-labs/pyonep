# ==============================================================================
# exceptions.py
# exception handler for Exosite HTTP JSON RPC API library (man, alphabet soup)
# ==============================================================================
#
# Tested with python 2.6
#
# Copyright (c) 2010, Exosite LLC
# All rights reserved.
#
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


class ProvisionException(OneException):
    def __init__(self, provision_response):
        self.response = provision_response

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{0} {1}".format(self.response.status(), self.response.reason())
