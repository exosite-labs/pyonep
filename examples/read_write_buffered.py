#!/usr/bin/python
#==========================================================================
# read_write_buffered.py
# Simple use cases of the pyonep package communicating/interacting with the
# Exosite Data Platform
#==========================================================================
#
# Tested with python 2.6
#
# Copyright (c) 2010, Exosite LLC
# All rights reserved.
#

import time
import sys
import random
from pyonep.datastore import Datastore
import json

# put a CIK here. register on portals.exosite.com and +Add Device to get one
cik = "PUTYOUR40CHARACTERCIKHERE"

# dataport configuration - if the dataport doesn't exist,
# it will be auto-created with these params
dataport_config = {
    # use string format (float, int are also supported)
    'format': 'string',
    # preprocess is pretty flexible - can preprocess raw data
    # with constants and other data
    'preprocess': [['add', 1], ['mul', 2]],
    # allow maximum data retention
    'count': 'infinity',
    # keep data for as long as possible
    'duration': 'infinity',
    # allow data to be visible by the parent
    'visibility': 'parent'
}
# transport configuration - where this script will talk to and how it will talk
transport_config = {
    # API server name or IP
    'host': 'm2.exosite.com',
    # API server port for HTTP
    'port': '80',
    # Whether to use https (if True set port to 443)
    'https': False,
    # URL that the API handler is on
    'url': '/onep:v1/rpc/process',
    # API server port for HTTP
    'timeout': 3
}
# datastore configuration - how the library will buffer/cache
# read/write/record activities
datastore_config = {
    # buffer up to N bytes for writes to platform
    'write_buffer_size': 1024,
    # cache up to N bytes for reads from platform
    'read_cache_size': 1024,
    # if read from same RID > N seconds from last, get fresh
    'read_cache_expire_time': 3,
    # log level (debug, info, warn, error)
    'log_level': 'warn'
}
# configures how often our write buffer will be processed for sending
interval = 3


def caseCreateDataport():
    print "++caseCreateDataport++"
    reporter = Datastore(cik,
                         interval,
                         dataport_config,
                         datastore_config,
                         transport_config)
    status, message = reporter.createDataport(
        alias='V1',
        format="float",
        name=None,
        preprocess=[['add', 1]],
        count=10,
        duration="infinity",
        visibility="parent")


def caseWrite():
    print "++caseWrite++"
    reporter = Datastore(cik,
                         interval,
                         dataport_config,
                         datastore_config,
                         transport_config)
    reporter.start()
    val = random.randint(1, 100)
    print "Writing %i real-time as raw data to One Platform \
(value may be pre-processed before storing).\r\n" % val
    try:
        # During 'interval' seconds, only the latest write call will be used
        # for a given alias.
        reporter.write('X1', val)
    except (KeyboardInterrupt, SystemExit):
        reporter.stop(True)
        sys.exit(0)
    reporter.stop(True)


def caseRead():
    print "++caseRead++"
    reporter = Datastore(cik,
                         interval,
                         dataport_config,
                         datastore_config,
                         transport_config)
    reporter.start()
    print "Read is sleeping for %i seconds to allow write buffer \
to flush." % interval
    time.sleep(interval)
    try:
        # this will read back value of whatever was in the 1P before writing,
        # and will store the value in cache
        print "Read: ", reporter.read('X1')
    except (KeyboardInterrupt, SystemExit):
        reporter.stop(True)
        sys.exit(0)
    reporter.stop(True)


def caseRecordOffset():
    print "++caseRecordOffset++"
    reporter = Datastore(cik,
                         interval,
                         dataport_config,
                         datastore_config,
                         transport_config)
    reporter.start()
    print "Writing multiple values by historical offset as raw data \
to One Platform (values may be pre-processed before storing).\r\n"
    try:
        reporter.record('X2', [[-3, 1], [-2, 2], [-1, 3]])
    except (KeyboardInterrupt, SystemExit):
        reporter.stop(True)
        sys.exit(0)
    reporter.stop(True)


def caseRecord():
    print "++caseRecord++"
    reporter = Datastore(cik,
                         interval,
                         dataport_config,
                         datastore_config,
                         transport_config)
    reporter.start()
    val = random.randint(1, 100)
    print "Writing %i historically as raw data to One Platform (value may be \
pre-processed before storing).\r\n" % val
    try:
        # put data to the record buffer
        reporter.record('X2', [[int(time.time()), val]])
    except (KeyboardInterrupt, SystemExit):
        reporter.stop(True)
        sys.exit(0)
    reporter.stop(True)


if __name__ == '__main__':
    level = datastore_config['log_level']
    print "Setting library log level to ", level
    print
    # run one or more of the following calls
    caseRecord()
    caseRecordOffset()
    caseWrite()
    caseRead()
    caseCreateDataport()
