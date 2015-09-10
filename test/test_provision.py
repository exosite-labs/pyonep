# -*- coding: utf-8 -*-
# pylint: disable=W0312
'''Test pyonep library.'''
from __future__ import unicode_literals
import json
import md5
import os
from unittest import TestCase

# import vcr
import requests

from pyonep import onep

CIK_FNTN_URL = 'https://cik.herokuapp.com/api'
print(os.path.abspath(__file__))
CIK_FNTN_VENDOR_ID = md5.md5(os.path.abspath(__file__)).hexdigest()
print("VENDOR_ID: {0}".format(CIK_FNTN_VENDOR_ID))
# sys.exit()
CIK_FNTN_CASS = 'vcr_cassettes/cik_fntn_cassette.yaml'
# myvcr = vcr.VCR(
#     match_on=['method', 'scheme', 'uri', 'query', 'body'],
#     record_mode='new_episodes'
# )

class TestProvision(TestCase):
    """
        Test pyonep provisioning methods.
    """
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        # with myvcr.use_cassette(CIK_FNTN_CASS):
        r = requests.get(CIK_FNTN_URL+'/create?vendor') #='+CIK_FNTN_VENDOR_ID)
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

    # @myvcr.use_cassette('vcr_cassettes/test_move.yaml')
    def test_move(self):
        '''Test move command'''
        #    self.cik
        #       |
        #      cik2
        #       |
        #      cik3
        cik2, _ = self.makeClient(self.cik)
        _, rid3 = self.makeClient(cik2)

        # move cik3 to self.cik
        ok, response = self.onep.move(self.cik, rid3, self.rid)
        print(response)

        # after move, should be
        #    self.cik
        #     |    |
        #    cik3 cik2
        self.assertTrue(ok, 'move succeeded')

    # @myvcr.use_cassette('vcr_cassettes/test_provision_example.yaml')
    def test_provision_example(self):
        '''Test provisioning example code'''
        from examples import provisioning
        clonecik, clonerid = self.makeClient(self.cik)
        r = provisioning.provision_example(
            vendorname=self.vendorname,
            vendortoken=self.vendortoken,
            clonerid=clonerid,
            portalcik=self.cik,
            portalrid=self.rid
        )
        self.assertTrue(r, "provisioning example runs without error")
