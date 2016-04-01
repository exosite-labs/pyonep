# -*- coding: utf-8 -*-
# pylint: disable=W0312
"""Test pyonep library."""
from __future__ import unicode_literals
from unittest import TestCase

import requests

from pyonep import onep


CIK_FNTN_URL = 'https://cik.herokuapp.com/api'


def create_temporary_client():
    """Create a temporary client, returning a TestClient object."""
    return TestBase.createTestClient()


class TestClient():
    def __init__(self, config):
        self.config = config
        self.cik = config['cik']
        self.rid = config['rid']
        self.vendor = config['vendor']
        self.vendortoken = config['vendortoken']


class TestBase(TestCase):
    """
        Base class for PyOnep tests
    """

    # not a test
    __test__ = False
    _multiprocess_can_split_ = True

    @classmethod
    def createTestClient(cls):
        r = requests.get(CIK_FNTN_URL+'/create?vendor', timeout=15.)
        r.raise_for_status()
        config = r.json()
        return TestClient(config)

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        r = requests.get(CIK_FNTN_URL+'/create?vendor', timeout=15.)
        r.raise_for_status()
        cls.config = r.json()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """Create a device in the portal to test"""
        self.portalcik = self.config['cik']
        self.vendorname = self.config['vendor']
        self.vendortoken = self.config['vendortoken']
        self.onep = onep.OnepV1()
        isok, response = self.onep.create(
            self.portalcik,
            'client',
            {
                'writeinterval': 'inherit',
                'name': 'testclient',
                'visibility': 'parent',
                'limits': {
                    'dataport': 'inherit',
                    'datarule': 'inherit',
                    'dispatch': 'inherit',
                    'disk': 'inherit',
                    'io': 'inherit',
                    'share': 'inherit',
                    'client': 'inherit',
                    'sms': 'inherit',
                    'sms_bucket': 'inherit',
                    'email': 'inherit',
                    'email_bucket': 'inherit',
                    'http': 'inherit',
                    'http_bucket': 'inherit',
                    'xmpp': 'inherit',
                    'xmpp_bucket': 'inherit'}
            })
        self.assertTrue(isok, 'created test client')
        self.rid = response
        isok, response = self.onep.info(
            self.portalcik,
            self.rid,
            {'key': True}
        )
        self.assertTrue(isok, 'got key for test client')
        self.cik = response['key']

    def tearDown(self):
        """Clean up any test client"""
        self.onep.drop(self.portalcik, self.rid)

    def makeClient(self, cik, name=None, desc=None):
        """
            This is not a test.
            This function is a test-helper and should
            probably be put into pyonep.

            It returns a tuple: (cik, rid).
        """
        if desc is None:
            # default description
            desc = {'limits': {'client': 'inherit',
                               'dataport': 'inherit',
                               'datarule': 'inherit',
                               'disk': 'inherit',
                               'dispatch': 'inherit',
                               'email': 'inherit',
                               'email_bucket': 'inherit',
                               'http': 'inherit',
                               'http_bucket': 'inherit',
                               'share': 'inherit',
                               'sms': 'inherit',
                               'sms_bucket': 'inherit',
                               'xmpp': 'inherit',
                               'xmpp_bucket': 'inherit'}
            }
        if name is not None:
            desc['name'] = name
        isok, response = self.onep.create(cik, 'client', desc)
        if not isok:
            raise "Failed to create client. ONE Platform said '{0}'".format(response)
        rid = response

        isok, response = self.onep.info(
            cik,
            rid,
            {'key': True}
        )
        if not isok:
            raise "Failed to retrieve CIK. ONE Platform said '{0}'".format(response)
        cik = response['key']
        return cik, rid
