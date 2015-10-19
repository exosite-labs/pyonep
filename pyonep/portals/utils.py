"""
    Just a collection of helper functions to 
    do common tasks.
"""
# pylint: disable=W0312

import requests, time, json
from urllib.parse import quote_plus

def dictify_device_meta(device_object):
    try:
        if isinstance(device_object['description']['meta'], str):
            device_object['description']['meta'] =\
                json.loads(device_object['description']['meta'])
    except ValueError as err:
        print("dictify: {0}".format(device_object['description']['meta']))
    return device_object

def get_map_url_and_timezone(address):
    """
        This function takes an address as input
        and returns a tuple of (timezone, google_map_url).
    """
    GOOGLE_API_URL='https://maps.googleapis.com/maps/api'

    linkurl = '{0}/geocode/json?address={1}&sensor=false'.format(
            GOOGLE_API_URL,quote_plus(address))
    linkblob = requests.get(linkurl).json()
    latlong = linkblob['results'][0]['geometry']['location']
    map_url = 'https://www.google.com/maps?q={0},{1}'.format(
                                    latlong['lat'], latlong['lng'])
    print('Link to map of address: {0}'.format(map_url))
    
    tzurl = '{0}/timezone/json?location={1},{2}&timestamp={3}'.format(
            GOOGLE_API_URL,latlong['lat'], latlong['lng'], int(time.time()))
    tzblob = requests.get(tzurl).json()
    tz = tzblob['timeZoneId']
    print("Timezone of address {0}".format(tz))
    return (tz, map_url)


