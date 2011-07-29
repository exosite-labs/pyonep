 ========================================
About pyonep
========================================
This project contains a package called "onepv1lib".  The onepv1lib package is an
API library with python bindings to the Exosite One Platform API.  The API is 
exposed over HTTP in a JSON RPC style interface.

Recommended with python 2.6 or later.

License is BSD, Copyright 2011, Exosite LLC (see LICENSE file)

========================================
Required Python Packages
========================================
****************************************
1) python-simplejson  (python 2.5 and earlier only)
****************************************
https://github.com/simplejson/simplejson

simplejson only necessary for python version 2.5 and earlier.  For python 2.6 
and later, the library uses the native "python-json" package.

========================================
Installation
========================================
1.) Unpack the distribution archive (if necessary)

2.) Navigate into the root "pyonep" directory

3.) Install the package:
	python setup.py install

4.) If you do not want to install the package, or cannot due to system 
limitations, simply copy the ./onepv1lib folder into the same folder as your
script.  Or, alternatively, add the ./onepv1lib folder to your sys.path.

========================================
Quick Start
========================================
To use the pyonep Exosite API, import per:
	from onepv1lib.datastore import Datastore

This library requires you to initialize with the following parameters:</br>
--) cik: a 40 character "client interface key" that authenticates your 
        application with the One Platform
--) interval: number of seconds between One Platform publish activity.  Even if
        your application calls the "write" function more often than this 
        interval, the data will be grouped to be published at this interval 
--) autocreate: dataport parameter setup - see the One Platform documentation
        for more information about dataport parameters.
--) datastore_config: local write buffer and read cache parameter setup
--) transport_config: Exosite server parameter setup

For examples, reference example scripts in the ./onepv1lib/examples/ folder.  
Note that to run the examples without installing the pyonep package, the 
example script must be located in the root folder (with ./onepv1lib as a 
sub-folder).

For more information on the API, reference Exosite online documentation.

========================================
Release Info
========================================

Release 1.0
----------------------------------------
--) initial public version
