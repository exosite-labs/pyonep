# -*- coding: utf-8 -*-
"""Test pyonep RPC"""
from __future__ import unicode_literals
import doctest
import re

from nose.plugins.multiprocess import MultiProcess

from pyonep import onep
from test import test_base

class TestRPC(test_base.TestBase):
    """
        Test pyonep RPC methods
    """
    # yes, test this
    __test__ = True
    _multiprocess_can_split_ = True

    def test_doc_examples(self):
        """Test documentation examples"""
        doctest.testfile('../docs/examples.md')

    def test_http(self):
        """Test http switch"""
        onephttp = onep.OnepV1(port='80', https=False)
        ok, info = onephttp.info(self.cik,
                                 {'alias': ''},
                                 options={'basic': True})
        self.assertTrue(ok, 'info call succeeded')
        self.assertEqual(info['basic']['status'], 'activated')

    def test_token(self):
        """Test token grant/use"""
        # grant token to cik
        ok, result = self.onep.grant(
            self.cik,
            self.rid,
            { self.rid: [ "read", "write" ] },
            ttl=1000)

        self.assertTrue(ok, 'grant succeeded')
        token = result
        self.assertEqual(len(token), 40, 'token is correct length')

        child_rid = self.makeDataport(self.cik, 'string', 'message', 'Message')

        # write a value
        ok, result = self.onep.write({'token': token}, {'alias': 'message'}, '你好')
        self.assertTrue(ok, 'write to dataport using token')

        # read value back
        ok, result = self.onep.read({'token': token}, {'alias': 'message'}, {'limit': 1})
        self.assertEqual(result[0][1], '你好')
        self.assertTrue(ok, 'read back from dataport using token')


    def test_move(self):
        """Test move command"""
        #    self.cik
        #       |
        #      cik2
        #       |
        #      cik3
        cik2, _ = self.makeClient(self.cik)
        _, rid3 = self.makeClient(cik2)

        # move cik3 to self.cik
        ok, response = self.onep.move(self.cik, rid3, self.rid)

        # after move, should be
        #    self.cik
        #     |    |
        #    cik3 cik2
        self.assertTrue(ok, 'move succeeded')

    def test_create(self):
        """Test create API call"""
        isok, response = self.onep.create(
            self.cik,
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
        client_rid = response
        self.assertTrue(isok, 'client creation succeeded')
        self.assertTrue(re.match("^[0-9a-f]{40}$", client_rid), 'rid is formatted correctly')

        isok, response = self.onep.info(
            self.cik,
            client_rid,
            {'key': True}
        )
        client_cik = response['key']

        # Add a dataport
        isok, response = self.onep.create(
            client_cik,
            'dataport',
            {
                'format': 'string',
                'retention': {
                    'count': 'infinity',
                    'duration': 'infinity',
                },
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
                    'xmpp_bucket': 'inherit',
                }
            }
        )
        dataport_rid = response
        self.assertTrue(isok, 'dataport creation succeeded')
        self.assertTrue(re.match("^[0-9a-f]{40}$", dataport_rid), 'rid is formatted correctly')

    def test_drop(self):
        """Test drop API call"""
        client_cik, client_rid = self.makeClient(self.cik)
        isok, response = self.onep.drop(self.cik, client_rid)
        self.assertTrue(isok, 'client drop succeeded')
        isok, response = self.onep.info(self.cik, client_rid)
        self.assertFalse(isok, 'dropped client was really dropped')
