# -*- coding: utf-8 -*-
# pylint: disable=W0312
'''Test pyonep library.'''
from __future__ import unicode_literals
import requests, json, md5, os, sys
# import vcr
from unittest import TestCase
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
        TestClase class for testing pyonep provisioning methods.
    """
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        # with myvcr.use_cassette(CIK_FNTN_CASS):
        r = requests.get(CIK_FNTN_URL+'/create?vendor') #='+CIK_FNTN_VENDOR_ID)
        print(r.status_code, r.text)
        cls.config =r.json()
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
        self.clonecik = response['key']

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
        cik1 = self.config['cik']
        rid1 = self.config['rid']
        #      cik1
        #       |
        #      cik2
        #       |
        #      cik3
        cik2, _ = self.makeClient(cik1)
        _, rid3 = self.makeClient(cik2)

        # move cik3 to self.cik
        ok, response = self.onep.move(cik1, rid3, rid1)
        print(response)

        # after move, should be
        #      cik1
        #     |    |
        #    cik3 cik2
        self.assertTrue(ok, 'move succeeded')






    # @myvcr.use_cassette('vcr_cassettes/test_provision_example.yaml')
    def test_provision_example(self):
        '''Test provisioning example code'''
        from examples import provisioning
        c = {}
        c['vendorname'] = self.vendorname
        c['vendortoken'] = self.vendortoken
        c['clonecik'] = self.clonecik
        c['portalcik'] = self.portalcik
        r = provisioning.provision_example(c)
        self.assertTrue(r, "provisioning example runs without error")
