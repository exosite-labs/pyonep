#!/usr/bin/python
import time,sys,random,math
from onepv1lib.datastore import Datastore

cik = "de8dae710a6465cf72c4744bb382eeecf9ede5ba" #staging
autocreate = {'format':'string','preprocess':[['add',1],['mul',2]],'count':'infinity','duration':'infinity','visibility':'parent'}
transport_config = {'host':'96.126.102.194','port':'80','url':'/api:v1/rpc/process','timeout':3}
datastore_config = {'write_buffer_size':1024,'read_cache_size':1024,'read_cache_expire_time':5,'log_level':'info'}
interval   = 5 # check/write buffer every five seconds

def caseWrite():
  reporter = Datastore(cik,interval,autocreate,datastore_config,transport_config)
  reporter.start()
  val = 0
  while True:
    try:
      # During 'interval' seconds, new write call will replace the old value with the new one in write(alias,value) for that alias.
      reporter.write('X1',val)
      #while not reporter.write('X1',val): # Ensure the data is in the buffer 
      #  pass
      val += 1
      time.sleep(1)       
    except (KeyboardInterrupt, SystemExit):
      reporter.stop()
      sys.exit(0)

def caseRead():
  reporter = Datastore(cik,1,autocreate,datastore_config,transport_config)
  reporter.start()
  reporter.write('X1',67)
  print reporter.read('X1')
  reporter.write('X1',89)
  time.sleep(3)
  print reporter.read('X1')
  time.sleep(5) 
  print reporter.read('X1') 
  reporter.stop(True)
  
def caseRecordOffset():
  reporter = Datastore(cik,interval,autocreate,datastore_config,transport_config)
  reporter.start()
  reporter.record('X2',[[-3,1],[-2,2],[-1,3]])
  reporter.stop(True)
  
def caseRecord():
  reporter = Datastore(cik,interval,autocreate,datastore_config,transport_config)
  reporter.start()
  v = 0
  while True:    
    try:
      v += 1
      reporter.record('X2',[[int(time.time()),v]]) # put data to the record buffer
      time.sleep(1)   
    except (KeyboardInterrupt, SystemExit):
      reporter.stop(True)
      sys.exit(0)

if __name__ == '__main__':
  #caseWrite()
  #caseRecord()
  #caseRecordOffset()
  caseRead()

  
