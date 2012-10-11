#!/usr/bin/env python

import random
import time

import onep

o = onep.OnepV1()

# devices for demo
CIK_TEMP='f005386eb0e58e62c99a26155e446a66ad6f7e4d' 
CIK_HUMIDITY='49e4088319cdd64bb6be2cffa68f329c1cc41344'


def create_dataports(cik, prefix="Temperature"):
    '''Create dataports for a sensor.'''
    o.create_dataport(cik,
            format="float",
            name=prefix,
            defer=True)

    o.create_dataport(cik,
            format="float",
            name="ThresholdLow",
            defer=True)

    o.create_dataport(cik,
            format="float",
            name="ThresholdHigh",
            defer=True)

    for i in range(3):
        o.create_dataport(cik,
            format="integer",
            name=prefix + "Reg" + str(i),
            defer=True)

    o.create_dataport(cik,
            format="integer",
            name="config",
            defer=True)

    # send the request
    responses = o.send_deferred(cik)

    for request, success, response in responses:
        if success:
            print("Create request succeeded")
            # add an alias
            name = request['arguments'][1]['name']
            rid = response
            o.map(cik, rid, name, defer=True)
        else: 
            print("Create request failed")
        print request, response

    if o.has_deferred(cik):
        responses = o.send_deferred(cik)
        for request, success, response in responses:
            if success:
                print("Map request succeeded")
            else:
                print("Map request failed")
            print request, response


def drop_dataports(cik):
    '''Drop all dataports for a sensor.'''
    success, response = o.listing(cik, ["dataport"])
    if success:
        for rid in response[0]:
            o.drop(cik, rid, defer=True)

        # send the request
        if o.has_deferred(cik):
            responses = o.send_deferred(cik)

            for request, success, response in responses:
                if success:
                    print("Drop succeeded")
                else: 
                    print("Drop failed")
                print request, response

    else:
        print("Request for listing failed")


def reset():
    '''Drop and recreate dataports for demo devices'''
    # drop dataports for both sensors
    drop_dataports(CIK_TEMP)
    drop_dataports(CIK_HUMIDITY)

    # create temperature sensor
    create_dataports(CIK_TEMP, "Temperature")

    # create humidity sensor
    create_dataports(CIK_HUMIDITY, "Humidity")


def send_data_loop():
    while True:
        temp = random.normalvariate(25, 0.05)
        humidity = random.normalvariate(50, 1)
        print CIK_TEMP
        success, response = o.write(CIK_TEMP, 
                                    {'alias':'Temperature'}, 
                                    temp)
        print success, response
        print CIK_HUMIDITY
        success, response = o.write(CIK_HUMIDITY, 
                                    {'alias':'Humidity'}, 
                                    humidity)
        print success, response
        print "temp: {0}, \thumidity: {1}".format(temp, humidity)
        time.sleep(5)


reset()
send_data_loop()
