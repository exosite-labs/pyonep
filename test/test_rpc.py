# -*- coding: utf-8 -*-
# pylint: disable=W0312
'''Test pyonep RPC'''
from __future__ import unicode_literals
import doctest
import re

from test import test_base


class TestRPC(test_base.TestBase):
    """
        Test pyonep RPC methods
    """
    # yes, test this
    __test__ = True

    def test_doc_examples(self):
        '''Test documentation examples'''
        doctest.testfile('../docs/examples.md')

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

    def test_create(self):
        '''Test create API call'''
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
        rid = response
        self.assertTrue(isok, 'client creation succeeded')
        self.assertTrue(re.match("^[0-9a-f]{40}$", rid), 'rid is formatted correctly')
