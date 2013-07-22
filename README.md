About pyonep
============

This project contains a package called "pyonep".  The pyonep package is an
API library with python bindings to the Exosite One Platform API.  The API is 
exposed over HTTP in a JSON RPC style interface.

Recommended with python 2.6 or later.

License is BSD, Copyright 2011, Exosite LLC (see LICENSE file)

Required Python Packages
------------------------

1.) python-simplejson  (python 2.5 and earlier only)

https://github.com/simplejson/simplejson

Simplejson only necessary for python version 2.5 and earlier.  For python 2.6 
and later, the library uses the native "python-json" package.

Installation
------------

1.) Unpack the distribution archive (if necessary)

2.) Navigate into the root "pyonep" directory

3.) Install the package:

```bash

    git clone https://github.com/exosite-labs/pyonep
	python setup.py install
```

If you'd rather not install the package, you can also copy the 
./pyonep/pyonep folder into the same folder as your script, or 
add the ./pyonep/pyonep folder to your sys.path.


Getting A CIK
-------------

Access to the Exosite API requires a Client Information Key (CIK). If 
you're just getting started with the API and have signed up with a 
community portal, here's how you can find a CIK:

1.) Log in: https://portals.exosite.com

2.) Click on *devices* on the left

3.) Click on a device to open its properties

4.) The device's CIK is a 40 character alphanumeric identifier labeled CIK:

Once you have a CIK, you can substitute it in the examples below.


Usage
-----

Here's how to get information about a device:

```python

from pyonep import onep
from pprint import pprint

o = onep.OnepV1()

cik = 'INSERT_CIK'

pprint(o.info(
    cik,
    {'alias': ''}))
```


Buffered Access
---------------

The pyonep library includes a module that provides buffered access to the
RPC API, which may offer better performance in some cases.

See examples/read\_write\_record.py for more details. 


Example Scripts
---------------

Examples are located in examples/. To run them, first modify them with your
device information.

- get_info.py - uses the onep module to send a single command

- mult_cmd.py - uses the onep module to send

- read_write_record.py - uses the datastore module for buffered access to the API,
    which can be higher performance in some scenarios 

- provisioning.py - uses the provision module to provision some 

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
