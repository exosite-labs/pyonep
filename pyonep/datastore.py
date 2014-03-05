#==============================================================================
# datastore.py
# Buffering, caching and batch functions for access to the Exosite Data
# Platform using the JSON RPC API over HTTP.
# This layer was written so that a system with many subcriber/provider tasks
# could simulataneously access the platform efficiently.
#==============================================================================
#
# Tested with python 2.6
#
# Copyright (c) 2014, Exosite LLC
# All rights reserved.
#

import threading
import time
import sys
import logging
from onep import OnepV1
from exceptions import OneException

# setup default configurations
transport_config = {'host': 'm2.exosite.com',
                    'port': '80',
                    'url': '/onep:v1/rpc/process',
                    'https': False,
                    'timeout': 3}
datastore_config = {'write_buffer_size': 1024,
                    'read_cache_size': 1024,
                    'read_cache_expire_time': 5,
                    'log_level': 'debug'}

log = logging.getLogger(__name__)
lock = threading.Lock()


class Datastore():
    def __init__(self,
                 cik,
                 interval,
                 autocreate=False,
                 config=datastore_config,
                 transport=transport_config):
        self._liveBuffer = dict()
        self._recordBuffer = dict()
        self._aliasDict = dict()
        self._cache = dict()
        self._cacheCount = 0
        self._recordCount = 0
        self._auto = autocreate
        self._config = config
        if 'https' in transport:
            transport['https'] = False
        self._conn = OnepV1(transport['host'],
                            transport['port'],
                            transport['url'],
                            transport['https'],
                            transport['timeout'])
        self._cik = cik
        if interval < 1:
            interval = 1
        self._interval = interval

    def __bufferCount(self):
        return len(self._liveBuffer) + self._recordCount

    def __isBufferFull(self):
        return self.__bufferCount() >= self._config['write_buffer_size']

    def __isLiveBufferEmpty(self):
        if self._liveBuffer:
            return False
        else:
            return True

    def __forceTerminate(self):
        if self._killed and self._forceterminate:
            self._liveBuffer.clear()
            return True
        else:
            return False

    # One platform queries below

    def __lookup(self, alias, forcequery=False):
        if (not forcequery) and alias in self._aliasDict:
            return self._aliasDict[alias]
        else:
            status, res = self._conn.lookup(self._cik, 'alias', alias)
            if not status:
                self._aliasDict[alias] = False
                return False
            else:
                self._aliasDict[alias] = res
                return res

    def __read(self,
               alias,
               count=1,
               forcequery=False,
               sort='desc',
               starttime=None,
               endtime=None):
        rid = self.__lookup(alias, forcequery)
        if None != starttime and None != endtime:
            status, res = self._conn.read(
                self._cik,
                rid,
                {"starttime": starttime,
                 "endtime": endtime,
                 "limit": count,
                 "sort": sort})
        else:
            status, res = self._conn.read(self._cik,
                                          rid,
                                          {"limit": count,
                                           "sort": sort})
        if not status:
            raise OneException(
                "Error message from one platform (read): %s" % res)
        return res

    def __record(self, alias, entries):
        rid = self.__lookup(alias)
        record_status, record_message = self._conn.record(self._cik,
                                                          rid,
                                                          entries)
        if not (True == record_status and 'ok' == record_message):
            msg = "Error message from one platform (record): %s"
            raise OneException(msg % record_message)
        return True

    def __writegroup(self, entries):
        data = list()
        for (alias, value) in entries:
            rid = self.__lookup(alias)
            data.append([rid, value])
        write_status, write_message = self._conn.writegroup(self._cik, data)
        if not (True == write_status and 'ok' == write_message):
            msg = "Error message from one platform (write): %s,%s"
            raise OneException(msg % (value, write_message))
        return True

    def __createDataport(self,
                         alias,
                         name=None,
                         format="string",
                         preprocess=[],
                         count="infinity",
                         duration="infinity",
                         visibility='parent'):
        if None == name:
            name = alias
        desc = {"format": format,
                "name": name,
                'visibility': visibility,
                "retention": {"count": count,
                              "duration": duration},
                "preprocess": preprocess}
        create_status,rid = self._conn.create(self._cik, "dataport", desc)
        if create_status:
            map_status, map_message = self._conn.map(self._cik, rid, alias)
            if map_status:
                self._aliasDict[alias] = rid
                return True
            else:
                self._conn.drop(self._cik, rid)
                log.error(map_message)
                return False
        else:
            log.error(rid)
            return False

    def __checkDataportExist(self, alias):
        if self.__lookup(alias):
            return True
        else:
            if self._auto:
                if not self.__createDataport(
                        alias=alias,
                        format=self._auto['format'],
                        preprocess=self._auto['preprocess'],
                        count=self._auto['count'],
                        duration=self._auto['duration'],
                        visibility=self._auto['visibility']):
                    raise OneException("Fail to create dataport.")
                return True
            else:
                m = "Data source does not exist while not in AUTO_CREATE mode."
                log.warn(m)
                return False

    # Write buffer processing below

    def __processJsonRPC(self):
        while not self.__forceTerminate():
            time.sleep(self._interval)
            livedata = list()
            lock.acquire()
            try:
                timestamp = int(time.time())
                aliases = self._liveBuffer.keys()
                for alias in aliases:
                    value = self._liveBuffer[alias]
                    try:
                        # create datasource if necessary
                        if self.__checkDataportExist(alias):
                            # Move to live data
                            livedata.append([alias, value])
                            msg = "Data to be written (alias,value): ('%s',%s)"
                            log.debug(msg % (alias, value))
                    except OneException:
                        # catch exception, add to recordBuffer
                        if not alias in self._recordBuffer:
                            self._recordBuffer[alias] = list()
                        self._recordBuffer[alias].append(
                            [timestamp, value, True])
                        self._recordCount += 1
                    finally:
                        del self._liveBuffer[alias]
            finally:
                self._liveBuffer.clear()
                lock.release()
            # write live data
            if livedata:
                timestamp = int(time.time())
                try:
                    self.__writegroup(livedata)
                    log.info("[Live] Written to 1p:" + str(livedata))
                except OneException:
                    # go to historical data when write live data failure
                    e = sys.exc_info()[1]
                    msg = "Exception While Writing Live Data: {0}"
                    log.error(msg.format(e.message))
                    log.debug("Previous Exception For: {0}".format(livedata))
                    lock.acquire()
                    try:
                        for (alias, value) in livedata:
                            if not alias in self._recordBuffer:
                                self._recordBuffer[alias] = list()
                            offset = True
                            self._recordBuffer[alias].append(
                                [timestamp, value, offset])
                            self._recordCount += 1
                    finally:
                        lock.release()
                except Exception:
                    e = sys.exc_info()[1]
                    log.exception("Unknown Exception While Writing Data")
            ## write historical data
            lock.acquire()
            try:
                aliases = self._recordBuffer.keys()
                curtime = int(time.time())
                for alias in aliases:
                    entries = self._recordBuffer[alias]
                    try:
                        if self.__checkDataportExist(alias):
                            recentry = list()
                            for entry in entries:
                                if True == entry[2]:  # offset mode
                                    offset = entry[0] - curtime
                                    if offset == 0:
                                        # Must be a negative number.
                                        offset = -1
                                    recentry.append([offset, entry[1]])
                                else:
                                    recentry.append([entry[0], entry[1]])
                            if recentry:
                                try:
                                    self.__record(alias, recentry)
                                    log.info("[Historical] Written to 1p: "
                                             + alias + ", " + str(recentry))
                                    self._recordCount -= len(entries)
                                    del self._recordBuffer[alias]
                                except OneException:
                                    e = sys.exc_info()[1]
                                    if e.message.find("datapoint") != -1:
                                        log.excption(e.message)
                                        self._recordCount -= len(entries)
                                        del self._recordBuffer[alias]
                        else:
                            del self._recordBuffer[alias]
                    except OneException:
                        e = sys.exc_info()[1]
                        log.error(e.message)
                        continue
            finally:
                lock.release()
            if self._killed and not self._recordBuffer:
                self._forceterminate = True

    # Read cache routines below

    def __addCacheData(self, alias, count, forcequery=False):
        if self.__isCacheFull():
            self.__clearCache()
        self._cache[alias] = dict()
        data = self.__refreshData(alias, count, forcequery)
        if data:
            self._cacheCount += 1
        return data

    def __isExpired(self, alias):
        try:
            expire = self._config['read_cache_expire_time']
            return int(time.time()) - self._cache[alias]['time'] > expire
        except:
            return True

    def __isCacheFull(self):
        return self._cacheCount >= self._config['read_cache_size']

    def __clearCache(self):
        self._cache.clear()
        self._cache = dict()
        self._cacheCount = 0

    def __refreshData(self, alias, count, forcequery=False):
        try:
            time.sleep(1)
            data = self.__read(alias,
                               count,
                               forcequery)
            self._cache[alias]['data'] = data
            self._cache[alias]['time'] = int(time.time())
            return data
        except OneException:
            e = sys.exc_info()[1]
            log.error(e.message)
        except Exception:
            e = sys.exc_info()[1]
            log.excpetion("Unknown Exception While Refreshing Data")
        return False

    # Public methods below

    def isThreadAlive(self):
        return self._thread.isAlive()

    def comment(self,
                alias,
                visibility,
                commentstr):
        rid = self.__lookup(alias)
        if rid:
            status, message = self._conn.comment(self._cik,
                                                 rid,
                                                 visibility,
                                                 commentstr)
            if status:
                return True
        return False

    def createDataport(self,
                       alias,
                       format,
                       name=None,
                       preprocess=[],
                       count=0,
                       duration=0,
                       visibility="public"):
        rid = self.__lookup(alias)
        if rid:
            return False, "Alias already existed."
        else:
            if self.__createDataport(alias,
                                     name,
                                     format,
                                     preprocess,
                                     count,
                                     duration,
                                     visibility):
                return True, True
            else:
                return False, "Failed to create Dataport."

    def read(self, alias, count=1, forcequery=False):
        if alias in self._cache:  # has cache data
            if self.__isExpired(alias) or count != len(self._cache[alias]['data']):
                return self.__refreshData(alias, count, forcequery)
            else:
                return self._cache[alias]['data']
        else:  # no cache data
            return self.__addCacheData(alias, count, forcequery)

    def record(self, alias, entries):
        if self.__isBufferFull() or not (self._auto or self.__lookup(alias)):
            return False
        lock.acquire()
        try:
            if not alias in self._recordBuffer:
                self._recordBuffer[alias] = list()
            for (t, value) in entries:
                recentry = [t, value, False]
                self._recordBuffer[alias].append(recentry)
        finally:
            lock.release()

    def restart(self):
        self.stop(force=True)
        self.start()

    def start(self, daemon=False):
        time.sleep(1)
        self._killed = False
        self._forceterminate = False
        self._thread = threading.Thread(target=self.__processJsonRPC)
        self._thread.setDaemon(daemon)
        self._thread.start()

    def stop(self, force=False):
        self._killed = True
        self._forceterminate = force

    def write(self, alias, value):
        if self.__isBufferFull() or not (self._auto or self.__lookup(alias)):
            return False
        else:
            lock.acquire()
            try:
                if alias in self._liveBuffer:
                    self._liveBuffer[alias] = value
                    msg = "Update the (alias,value) in buffer:%s,%s"
                    log.debug(msg % (alias, value))
                    return False
                else:
                    self._liveBuffer[alias] = value
            finally:
                lock.release()
            log.debug("Current buffer count: %s" % self.__bufferCount())
            log.debug("Add to buffer:%s,%s" % (alias, value))
            return True
