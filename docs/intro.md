Introduction
===============

The pyonep package is an API library with Python bindings to the
following Exosite One Platform APIs:

* [RPC API](https://github.com/exosite/docs/tree/master/rpc)
* [Provisioning/Device Management API](https://github.com/exosite/docs/tree/master/provision)

pyonep supports Python 2.5 through 3.3. Its license is BSD, Copyright 2014, Exosite LLC.

Here's an example:

```python
from pyonep import onep

o = onep.OnepV1()

cik = 'INSERT_CIK'
dataport_alias = 'INSERT_ALIAS'
val_to_write = '1'

o.write(
    cik,
    {"alias": dataport_alias},
    val_to_write,
    {})

isok, response = o.read(
    cik,
    {'alias': dataport_alias},
    {'limit': 1, 'sort': 'desc', 'selection': 'all'})

if isok:
    # expect Read back [[1374522992, 1]]
    print("Read back %s" % response)
else:
    print("Read failed: %s" % response)
```

To get started, check out our [Installation docs](install.html).
