#!/usr/bin/python
#==========================================================================
# read_write_record.py
# Simple use cases of the pyonep package communicating/interacting with the
# Exosite Data Platform
#==========================================================================
##
## Tested with python 2.6
##
## Copyright (c) 2010, Exosite LLC
## All rights reserved.
##

import time,sys,random,math
from pyonep.datastore import Datastore
import json

# put a 1P CIK here - register on portals.exosite.com and +Add Device to get one
cik = "PUTYOUR40CHARACTERCIKHERE"
# dataport configuration - if the dataport doesn't exist, it will be auto-created with these params
dataport_config = {'format':'string',               #use string format (float, int are also supported)
                    'preprocess':[['add',1],['mul',2]], #preprocess is pretty flexible - can preprocess raw data with constants and other data
                    'count':'infinity',             #allow maximum data retention
                    'duration':'infinity',          #keep data for as long as possible
                    'visibility':'parent'}          #allow data to be visible by the parent
# transport configuration - where this script will talk to and how it will talk
transport_config = {'host':'m2.exosite.com',        #API server name or IP
                    'port':'80',                    #API server port for HTTP
                    'url':'/api:v1/rpc/process',    #URL that the API handler is on
                    'timeout':3}                    #API server port for HTTP
# datastore configuration - how the library will buffer/cache read/write/record activities
datastore_config = {'write_buffer_size':1024,       #buffer up to N bytes for writes to platform
                    'read_cache_size':1024,         #cache up to N bytes for reads from platform
                    'read_cache_expire_time':3,     #if read from same RID > N seconds from last, get fresh
                    'log_level':'warn'}             #log level (debug, info, warn, error)
# configures how often our write buffer will be processed for sending
interval = 3

#===============================================================================
def caseCreateDataport():
#===============================================================================
  print "++caseCreateDataport++"
  reporter = Datastore(cik,interval,dataport_config,datastore_config,transport_config)
  status,message = reporter.createDataport(alias='V1',format="float",name=None,preprocess=[['add',1]],count=10,duration="infinity",visibility="parent")
  if status:
    commentstr = json.dumps({"unit":"C"})
    reporter.comment('V1','public',commentstr)

#===============================================================================
def caseWrite():
#===============================================================================
  print "++caseWrite++"
  reporter = Datastore(cik,interval,dataport_config,datastore_config,transport_config)
  reporter.start()
  val = random.randint(1, 100)
  print "Writing %i real-time as raw data to One Platform (value may be pre-processed before storing).\r\n" % val
  try:
    reporter.write('X1',val)                        # During 'interval' seconds, only the latest write call will be used for a given alias.
  except (KeyboardInterrupt, SystemExit):
    reporter.stop(True)
    sys.exit(0)
  reporter.stop(True)

#===============================================================================
def caseRead():
#===============================================================================
  print "++caseRead++"
  reporter = Datastore(cik,interval,dataport_config,datastore_config,transport_config)
  reporter.start()
  print "Read is sleeping for %i seconds to allow write buffer to flush." % interval
  time.sleep(interval)
  try:
    print "Read: ",reporter.read('X1')              # this will read back value of whatever was in the 1P before writing, and will store the value in cache
  except (KeyboardInterrupt, SystemExit):
    reporter.stop(True)
    sys.exit(0)
  reporter.stop(True)

#===============================================================================
def caseRecordOffset():
#===============================================================================
  print "++caseRecordOffset++"
  reporter = Datastore(cik,interval,dataport_config,datastore_config,transport_config)
  reporter.start()
  print "Writing multiple values by historical offset as raw data to One Platform (values may be pre-processed before storing).\r\n"
  try:
    reporter.record('X2',[[-3,1],[-2,2],[-1,3]])
  except (KeyboardInterrupt, SystemExit):
    reporter.stop(True)
    sys.exit(0)
  reporter.stop(True)

#===============================================================================
def caseRecord():
#===============================================================================
  print "++caseRecord++"
  reporter = Datastore(cik,interval,dataport_config,datastore_config,transport_config)
  reporter.start()
  val = random.randint(1, 100)
  print "Writing %i historically as raw data to One Platform (value may be pre-processed before storing).\r\n" % val
  try:
    reporter.record('X2',[[int(time.time()),val]])  # put data to the record buffer
  except (KeyboardInterrupt, SystemExit):
    reporter.stop(True)
    sys.exit(0)
  reporter.stop(True)

#===============================================================================
if __name__ == '__main__':
  print "================================="
  print "Running script read_write_record.py"
  print "================================="
  print "NOTE: Script is setting library log level to:",datastore_config['log_level']
  print
  # run one or more of the following calls
  caseRecord()
  caseRecordOffset()
  caseWrite()
  caseRead()
  caseCreateDataport()

