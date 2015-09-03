# -*- coding: utf-8 -*-
'''Test pyonep library.'''
from __future__ import unicode_literals
import sys
from pprint import pprint
import requests
import random
import string
import json

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

    def makeClient(self, cik):
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

    def test_move(self):
        '''Test move command'''
        vendorid = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
        r = requests.get('https://cik.herokuapp.com/api/create?vendor=' + vendorid)
        r.raise_for_status()
        response = json.loads(r.text)
        cik1 = response['cik']
        rid1 = response['rid']
        #      cik1
        #       |
        #      cik2
        #       |
        #      cik3
        cik2, rid2 = self.makeClient(cik1)
        cik3, rid3 = self.makeClient(cik2)

        # move cik3 to self.cik
        ok, response = self.onep.move(cik1, rid3, rid1)
        print(response)

        # after move, should be
        #      cik1
        #     |    |
        #    cik3 cik2
        self.assertTrue(ok, 'move succeeded')







    def test_example(self):
        '''Test provisioning example code'''
        from examples import provisioning
        c = config.copy()
        c['clonecik'] = self.cik
        c['portalcik'] = self.portalcik
        r = provisioning.provision_example(c)
        self.assertTrue(r, "provisioning example runs without error")
