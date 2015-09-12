# -*- coding: utf-8 -*-
# pylint: disable=W0312

"""Test provisioning module"""

from __future__ import unicode_literals

from nose.plugins.multiprocess import MultiProcess

from pyonep import onep
from test import test_base


class TestProvision(test_base.TestBase):
    """
        Test pyonep provisioning methods.
    """
    # yes, test this
    __test__ = True
    _multiprocess_can_split_ = True

    def test_provision_example(self):
        """Test provisioning example code"""
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
