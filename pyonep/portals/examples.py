#!/usr/bin/env python
# pylint: disable=W0312
from pyonep.portals.bindings import Bindings
from getpass import getpass
import sys

if sys.version_info[0] < 3:
    _input = raw_input
else:
    _input = input

def example():

    # This is how to instantiate a portals.bindings Bindings object
    # in interactive mode. It works basically the same way logging
    # in to an exosite Portals account works.
    (token, B) = Bindings.login_to_portal()
    PORTAL_CIK = B.portal_cik()

    print("\n\nYou have retrieved the following token:\n{0}\n\n".format(token))
    _input("Press any key to continue...")

    # for non-interactive mode, passing in user password to get a token and a logged-in 
    # Bindings object
    pw = getpass("You can write an application that uses passwords. Tell me yours: ")
    (token, B) = Bindings.login_to_portal(B.domain(),
                                          B.portal_name(),
                                          B.user(),
                                          pw)

    # for non-interactive mode, passing in token to get a logged-in Bindings object
    print("\n\nThis is an example Bindings object using a token from the first step. \
But you should know that it still makes calls to Exosite Portals.\n\n")
    print(      Bindings.login_to_portal( B.domain(),
                                          B.portal_name(),
                                          B.user(),
                                          token,
                                          use_token=True)
    )

    # for non-interactive mode, passing in token, id and rid to get a Bindings object that
    # doesn't need to make any Portals API calls
    _input("\n\nThis is an example Bindings object using a token from the first step. \
But you'll notice its really fast because it doesn't make any calls to Exosite Portals.\
\n\n\
Hit any key to continue...")
    print("Portal ID: {0}".format(B.portal_id()))
    (token, B) = Bindings.login_to_portal( B.domain(),
                                          B.portal_name(),
                                          B.user(),
                                          token,
                                          use_token=True,
                                          portal_id=B.portal_id())
    print(B)
    print("Here's your Portal CIK for '{0}': {1}".format(B.portal_name(), PORTAL_CIK))

if __name__ == '__main__':
    example()