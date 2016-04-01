"""
    Just a collection of helper functions to 
    do common tasks.
"""
# pylint: disable=W0312

import requests, time, json
try:
    # python 2
    from urllib import quote_plus
except:
    # python 3
    from urllib.parse import quote_plus

def dictify_device_meta(device_object):
    """ Input: Portals device object.
        Output: The same device object with the device meta
                converted to a python dictionary. """
    try:
        if isinstance(device_object['info']['description']['meta'], str):
            device_object['info']['description']['meta'] =\
                json.loads(device_object['info']['description']['meta'])
    except ValueError as err:
        print("dictify: {0}".format(err))
    return device_object

def stringify_device_meta(device_object):
    """ Input: Portals device object.
        Output: The same device object with the device meta
                converted to a python string. """
    try:
        if isinstance(device_object['info']['description']['meta'], dict):
            device_object['info']['description']['meta'] =\
                json.dumps(device_object['info']['description']['meta'])
    except ValueError as err:
        print("stringify: {0}".format(err))
    return device_object

