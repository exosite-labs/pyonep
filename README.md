About pyonep
============

The pyonep package is an API library with Python bindings to the 
following Exosite One Platform APIs:

- RPC: http://developers.exosite.com/display/OP/Remote+Procedure+Call+API
- Provisioning/Device Management: http://developers.exosite.com/pages/viewpage.action?pageId=1179705

Note that this library does not yet support the HTTP Data Interface. See
below for more information.

Supports Python 2.5 through 2.7

License is BSD, Copyright 2013, Exosite LLC (see LICENSE file)


Installation
------------

Install from Python package index: 

```bash

    $ pip install pyonep
```

Or install from source:

```bash

    $ git clone https://github.com/exosite-labs/pyonep
    $ cd pyonep
	$ python setup.py install
```

Note: If you'd rather not install the package, you can also copy the 
./pyonep/pyonep folder into the same folder as your script, or 
add the ./pyonep/pyonep folder to your sys.path. 

If you're running a version of Python earlier than 2.6 you'll need the 
python-simplejson package, available here: 

https://pypi.python.org/pypi/simplejson/


Getting A CIK
-------------

Access to the Exosite API requires a Client Information Key (CIK). If 
you're just getting started with the API and have signed up with a 
community portal, here's how you can find a CIK:

1.) Log in: https://portals.exosite.com

2.) Click on "devices" on the menu on the left

3.) Click on a device to open its properties

4.) The device's CIK is displayed on the left

Once you have a CIK, you can substitute it in the examples below.


Usage
-----

Write and read from a device dataport:

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

Get information about a device:

```python

from pyonep import onep
from pprint import pprint

o = onep.OnepV1()

cik = 'INSERT_CIK'
dataport_alias = 'INSERT_ALIAS'
val_to_write = '1'

# get information about the client 
pprint(o.info(
    cik,
    {'alias': ''}))
```

RPC API documentation:
http://developers.exosite.com/display/OP/Remote+Procedure+Call+API

Buffered Access
---------------

The pyonep library includes a module that provides buffered access to the
RPC API, which may offer better performance in some cases.

See examples/read\_write\_record.py for more details. 


Migration from version 0.3
--------------------------

If you were previously using version 0.3 and want to upgrade to 0.7.4,
you will need to update the package name in your scripts. The package name
was updated from onepv1lib to pyonep. For example:

```bash

from onepv1lib import onep
```

...should be changed to:

```bash

from pyonep import onep
```

A global search and replace of onepv1lib to pyonep in your scripts should 
work.


Example Scripts
---------------

Examples are located in examples/. To run them, first modify them with your
device information.

- read_write_direct.py - writes to a resource and then reads back

- get_info.py - gets information about a client

- mult_cmd.py - uses the onep module to send

- read_write_buffered.py - demonstrates use of the datastore module

- provisioning.py - demonstrates use of the provisioning API

Note that to run the examples without installing the pyonep package, the 
example script must be located in the root folder (with ./pyonep as a 
sub-folder).

For a example that fully exercises the RPC interface, see the exosite command
line interface: 

http://github.com/dweaver/exoline


General API Information
-----------------------

For more information on the API, see:

http://developers.exosite.com

HTTP Data Interface
-------------------

The HTTP Data Interface is a minimal HTTP API best suited to resource-constrained 
devices or networks. It is limited to reading and writing data one point at a 
time. An example of using Python to access this interface is here:

https://github.com/exosite-garage/python_helloworld

Here is a description of the API:

http://developers.exosite.com/display/OP/HTTP+Data+Interface+API
