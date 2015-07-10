# -*- coding: utf-8 -*-
'''Test pyonep library.'''
from __future__ import unicode_literals
import sys
from pprint import pprint

from unittest import TestCase

from pyonep import onep

try:
    from testconfig import config
except Exception as ex:
    print(ex)
    sys.stderr.write(
        'Copy testconfig.py.template to testconfig.py and set portalcik.')


class TestProvision(TestCase):
    def setUp(self):
        '''Create a device in the portal to test'''
        self.portalcik = config['portalcik']
        self.vendorname = config['vendorname']
        self.vendortoken = config['vendortoken']
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

    def test_example(self):
        '''Test provisioning example code'''
        from examples import provisioning
        c = config.copy()
        c['clonecik'] = self.cik
        c['portalcik'] = self.portalcik
        r = provisioning.provision_example(c)
        self.assertTrue(r, "provisioning example runs without error")
