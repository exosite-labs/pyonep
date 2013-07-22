from pyonep import onep
from pprint import pprint

o = onep.OnepV1()

cik = 'INSERT_CIK'

pprint(o.info(
    cik,
    {'alias': ''}))
