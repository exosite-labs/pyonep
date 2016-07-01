#!/usr/bin/python
#==============================================================================
# auth_token.py
# Demonstrates using token to do onep RPC request
#==============================================================================
#
# Tested with python 2.7.6
#

import argparse
import random
from pprint import pprint
from pyonep import onep

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demonstrates using token to do onep RPC request')
    parser.add_argument('token', help='Token of device')
    parser.add_argument('rid', help='resource rid')
    args = parser.parse_args()

    o = onep.OnepV1()
    auth = {'token': args.token}
    o.read(
        auth,
        args.rid,
        {'limit': 1, 'sort': 'desc', 'selection': 'all'},
        defer=True)

    o.listing(
        auth,
        ['client', 'token'],
        [],
        args.rid,
        defer=True)

    responses = o.send_deferred(auth)

    for call, success, response in responses:
        print
        print "Call:"
        pprint(call)
        print "Successful? {}".format(success)
        print "Response:"
        pprint(response)
