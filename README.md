About pyonep
============

The pyonep package is an API library with Python bindings to the 
following Exosite One Platform APIs:

- RPC: https://github.com/exosite/api/tree/master/rpc
- Provisioning/Device Management: https://github.com/exosite/api/tree/master/provision

__Warning__: version 0.8.0 requires changes to applications that used 
earlier versions of the provision module. See below for information about 
[migrating your applications from 0.7.x to 0.8.0](#migrating-to-080)

Note that this library does not yet support the HTTP Data Interface. See
below for more information.

Supports Python 2.5 through 3.3.

License is BSD, Copyright 2014, Exosite LLC (see LICENSE file)


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

Access to the Exosite API requires a Client Identification Key (CIK). 
If you're just getting started with the API and have signed up with a 
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
https://github.com/exosite/api/tree/master/rpc

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

Examples are located in [examples/](examples). To run them, first modify them with your
device information.

- [read_write_direct.py](examples/read_write_direct.py) - writes to a resource and then reads back

- [get_info.py](examples/get_info.py) - gets information about a client

- [mult_cmd.py](examples/mult_cmd.py) - uses the onep module to send

- [read_write_buffered.py](examples/read_write_buffered.py) - demonstrates use of the datastore module

- [provisioning.py](examples/provisioning.py) - demonstrates use of the provisioning API

Note that to run the examples without installing the pyonep package, the 
example script must be located in the root folder (with ./pyonep as a 
sub-folder).

For a Python example that fully exercises the RPC interface using the pyonep 
library, see the Exosite command line interface: 

http://github.com/exosite/exoline


General API Information
-----------------------

For more information on the API, see:

https://github.com/exosite/api

HTTP Data Interface
-------------------

The HTTP Data Interface is a minimal HTTP API best suited to resource-constrained 
devices or networks. It is limited to reading and writing data one point at a 
time. An example of using Python to access this interface is here:

https://github.com/exosite-garage/python_helloworld

The API is documented here:

https://github.com/exosite/api/tree/master/data

Migrating to 0.8.0
------------------

Version 0.8.0 includes some breaking changes to provision module API that will require changing applications. By following this guide these changes should not be too difficult.

- Previously, methods in provision module either returned a.) `True` (success) or `False` (failure) or b.) `<response body string>` (success) or `None` (failure). HTTP response details (e.g. status code) were not available to the caller without turning on logging and parsing stdout. With 0.8.0 all methods return a `ProvisionResponse` object with the following properties:

    - `ProvisionResponse.body` the response body, a string. The contents of this depend on the specific call, and may be of length 0. See [provision API documentation](https://github.com/exosite/api/tree/master/provision) for details.
    - `ProvisionResponse.status` the HTTP status code
    - `ProvisionResponse.isok` is a boolean representing whether the call succeeded (i.e. if the status code is < 400)

- Previously all exceptions associated with a call were being caught but not rethrown. With 0.8.0, HTTP exceptions are thrown to the caller. For example, if no connection is available, previously this would have written a message to the log and returned `None`. Now, a subclass of [`HTTPException`](http://docs.python.org/2/library/httplib.html#httplib.HTTPException) is thrown to the caller. This allows the caller to take appropriate action based on exactly what happened.

Here's an example of code based pyonep before 0.8.0:
```
import pyonep
provision = pyonep.Provision('http://m2.exosite.com', manage_by_cik=False)

# create a model
response = provision.model_create(vendortoken, model, clonerid, aliases=False)
if not response:
    print('Unknown error occurred in model_create')

# list models
model_list = provision.model_list(vendortoken)
if model_list is not None:
    print(model_list)
else:
    print('Unknown error occurred in model_list')
```

Here's how that would be written to work with 0.8.0+:
```
try:
  import httplib
except:
  # python 3
  from http import client as httplib

import pyonep

# the leading 'http://' is now optional but should be omitted
provision = pyonep.Provision('m2.exosite.com', manage_by_cik=False)

try:
    # create a model
    response = provision.model_create(vendortoken, model, clonerid, aliases=False)
    if not response.isok:
        print('Error in model_create: {0} {1}'.format(response.status, response.reason))

    # list models
    response = provision.model_list(vendortoken)
    if response.isok:
        print(response.body)
    else:
        print('Error in model_list: {0} {1}'.format(response.status, response.reason))
except httplib.HTTPException ex:
    print('HTTPException: {0}'.format(ex))
```

You can also ask the provision module to raise an exception for HTTP statuses of 400 and above by passing `raise_api_exceptions=True` to the `Provision` constructore. This can consolidate code that handles API errors for a large number of provision calls. See the [provisioning example](examples/provisioning.py) to see how to do this.
