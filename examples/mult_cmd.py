#!/usr/bin/python
#==============================================================================
# mult_cmd.py
# Demonstrates running two commands in one HTTP request using the RPC
#==============================================================================
#
# Tested with python 2.7.2
#

import argparse
import random
from pprint import pprint
from pyonep import onep


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demonstrate sending two commands in one request')
    parser.add_argument('cik', help='CIK of device')
    parser.add_argument('alias', help='alias of float format datasource')
    args = parser.parse_args()

    o = onep.OnepV1()

    o.write(args.cik,
            {"alias": args.alias},
            random.random() * 100,
            {},
            defer=True)
    o.read(
        args.cik,
        {'alias': args.alias},
        {'limit': 1, 'sort': 'desc', 'selection': 'all'},
        defer=True)

    responses = o.send_deferred(args.cik)

    for call, success, response in responses:
        print
        print "Call:"
        pprint(call)
        print "Successful? {}".format(success)
        print "Response:"
        pprint(response)
