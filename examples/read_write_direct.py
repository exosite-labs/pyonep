from pyonep import onep

o = onep.OnepV1()

cik = 'INSERT_CIK'
dataport_alias = 'INSERT_ALIAS'
val_to_write = '1'

# https://github.com/exosite/docs/tree/master/rpc#write
o.write(
    cik,
    {"alias": dataport_alias},
    val_to_write,
    {})

# https://github.com/exosite/docs/tree/master/rpc#read
isok, response = o.read(
    cik,
    {'alias': dataport_alias},
    {'limit': 1, 'sort': 'desc', 'selection': 'all'})

if isok:
    # expect Read back [[1374522992, 1]]
    print("Read back %s" % response)
else:
    print("Read failed: %s" % response)
