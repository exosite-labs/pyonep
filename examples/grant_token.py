#!/usr/bin/python
#==============================================================================
# grant_token.py
# Demonstrates grant the token
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
        description='Demonstrates grant the token')
    parser.add_argument('cik', help='CIK of device')
    parser.add_argument('rid', help='resource rid')
    parser.add_argument('ttl', help='Time to live')
    args = parser.parse_args()

    o = onep.OnepV1()
    o.grant(
        args.cik,
        args.rid,
        {
          args.rid: [
            "read",
            "write",
            "writegroup",
            "record",
            "flush",
            "wait",
            "info",
            "create",
            "move",
            "update",
            "listing",
            "drop",
            "usage",
            "map",
            "lookup",
            "unmap",
            "share",
            "revoke"
          ]
        },
        int(args.ttl),
        defer=True)

    responses = o.send_deferred(args.cik)

    for call, success, response in responses:
        print
        print "Call:"
        pprint(call)
        print "Successful? {}".format(success)
        print "Response:"
        pprint(response)
