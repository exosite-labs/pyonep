History
=======

0.9.1 (2014-10-29)
------------------

- fix the way provision exceptions are pulled in

0.9.0 (2014-09-19)
------------------

- use utf-8 for unicode support

0.8.4 (2014-04-09)
------------------

- add support for recordbatch

0.8.3 (2014-04-01)
------------------

- clear deferred requests on exception. 

0.8.2 (2014-02-11)
------------------

- update formatting to fit Python style guide (PEP 8)

0.8.1 (2014-02-11)
------------------

- support https, reuseconnection in provision.py
- don't log exceptions in onep.py, just raise them
- add example of onep.py error handling in examples/get_info.py

0.8.0 (2014-02-05)
------------------

- return ProvisionResult from provision methods to provide more 
  information about success/failure (breaking change)
- refactor provision.py to use httplib, and share code with onep.py.
- make version string available in pyonep.__version__, per PEP 396

0.7.13 (2014-01-31)
-------------------

- add support for flush options

0.7.12 (2014-01-27)
-------------------

- use generic RPC address

0.7.11 (2013-12-13)
-------------------

- support options for listing command

0.7.10 (2013-12-07)
-------------------

- add support for logging all request JSON

0.7.9 (2013-12-03)
------------------

- add support for Python 3.x

0.7.8 (2013-10-28)
-----------------

- add reuseconnection for performance


0.7.7 (2013-9-26)
-----------------

- add optional User-Agent string

0.7.6 (2013-8-18)
-----------------

- improved HTTP logging

0.7.5 (2013-8-12)
-----------------

- changed provisioning interface to manage by CIK 
  rather than vendor token by default
- fixed writegroup command
- added example code
- improved documentation 

0.7.4 (2013-7-22)
-----------------

- fixed support for python 2.5
- added example of using onep.py directly

0.7.3 (2013-7-19)
-----------------

- fixed issue with format in python 2.6
- fixed exception messages

0.7.2 (2013-7-19)
-----------------

- updated provisioning library for api change to use "meta" field
- updated provisioning library to use vendor token by default
- improved logging 
- fixed issue record offset is 0 in datastore
- reverted back to using distutils for python 2.6 support

0.7.1 (2013-7-18)
-----------------

- merge a few bug fixes from Exosite internal repo
- remove comment command
- fix multiple command example 

0.7.0 (2013-7-18)
-----------------

- renamed onepv1lib package to pyonep
- renamed onep_exceptions back to exceptions

0.6
---

- add usage command

0.5
---

- add support for https

0.4
---

- add support for sending multiple commands in a single request

0.3
---

- add provisioning library

0.2
---

- update example code

0.1
---

- initial version
