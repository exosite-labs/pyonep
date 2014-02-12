import pyonep
from pyonep import onep
from pprint import pprint

cik = 'YOUR CIK HERE'


def print_info(cik, alias='', httptimeout=30, repetitions=1):
    o = onep.OnepV1(httptimeout=httptimeout)
    try:
        for r in range(repetitions):
            o.info(
                cik,
                {'alias': alias},
                defer=True)
        responses = o.send_deferred(cik)
        pprint(responses)
    except pyonep.exceptions.JsonRPCRequestException as ex:
        print('JsonRPCRequestException: {0}'.format(ex))
    except pyonep.exceptions.JsonRPCResponseException as ex:
        print('JsonRPCResponseException: {0}'.format(ex))
    except pyonep.exceptions.OnePlatformException as ex:
        print('OnePlatformException: {0}'.format(ex))

print('Valid CIK, valid alias, but too small timeout')
print('(expect JsonRPCResponseException)')
print_info(cik, httptimeout=1, repetitions=100)

print('\nInvalid CIK')
print('(expect OnePlatformException)')
print_info('INTENTIONALLY BAD CIK')

print('\nValid CIK, invalid alias')
print('(expect no exception, just error response)')
print_info(cik, alias='this alias probably won\'t exist')

print('\nValid CIK, valid alias, good timeout')
print('(expect no exception, just good result)')
print_info(cik)
