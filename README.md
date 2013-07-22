About pyonep
============

The pyonep package is an API library with python bindings to the 
Exosite One Platform API.

http://developers.exosite.com/display/OP/API

Supports python 2.5 through 2.7

License is BSD, Copyright 2013, Exosite LLC (see LICENSE file)


Installation
------------

Install from python package index: 

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

If you're running a version of python earlier than 2.6 you'll need the 
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


Migration from version 0.3
--------------------------

If you were previously using version 0.3 and want to upgrade to 0.7.4,
you will need to update the package name in your scripts. The package name
was updated from onepv1lib to pyonep. For example:

```bash

from onepv1lib import pyonep
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

- get_info.py - uses the onep module to send a single command

- mult_cmd.py - uses the onep module to send

- read_write_record.py - demonstrates use of the datastore module

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
