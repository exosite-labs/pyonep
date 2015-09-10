# -*- coding: utf-8 -*-
# pylint: disable=W0312
'''Test pyonep RPC'''
from __future__ import unicode_literals

from test import test_base


class TestRPC(test_base.TestBase):
    """
        Test pyonep RPC methods
    """
    # yes, test this
    __test__ = True

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
