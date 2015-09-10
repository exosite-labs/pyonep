# -*- coding: utf-8 -*-
# pylint: disable=W0312
'''Test pyonep library.'''
from __future__ import unicode_literals
import json
import os
from unittest import TestCase

# import vcr
import requests

from pyonep import onep

CIK_FNTN_URL = 'https://cik.herokuapp.com/api'
print(os.path.abspath(__file__))
# sys.exit()
CIK_FNTN_CASS = 'vcr_cassettes/cik_fntn_cassette.yaml'
# myvcr = vcr.VCR(
#     match_on=['method', 'scheme', 'uri', 'query', 'body'],
#     record_mode='new_episodes'
# )

class TestBase(TestCase):
    """
        Base class for PyOnep tests
    """

    # not a test
    __test__ = False

    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        # with myvcr.use_cassette(CIK_FNTN_CASS):
        r = requests.get(CIK_FNTN_URL+'/create?vendor')
        print(r.status_code, r.text)
        cls.config = r.json()
        print("Here's the config from CIK Fountain:\n{0}".format(json.dumps(cls.config, indent=2)))

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        '''Create a device in the portal to test'''
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
        '''Clean up any test client'''
        self.onep.drop(self.portalcik, self.rid)

    def makeClient(self, cik):
        """
            This is not a test.
            This function is a test-helper and should
            probably be put into pyonep.
        """
        isok, response = self.onep.create(
            cik,
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
        rid = response
        isok, response = self.onep.info(
            cik,
            rid,
            {'key': True}
        )
        cik = response['key']
        return cik, rid
