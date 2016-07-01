History
=======

0.13.7 (2016-05-19)
-------------------

- add token support

0.13.6 (2015-10-21)
-------------------

- add Portals API support


0.13.5 (2015-09-21)
-------------------

- recover from exceptions in onephttp (issue in 0.13.0 - 0.13.4)


0.13.4 (2015-09-11)
-------------------

- build docstrings for read the docs site
- more PEP8 work


0.13.3 (2015-09-11)
-------------------

- fix another setup.py issue


0.13.2 (2015-09-11)
-------------------

- remove setup.py dependency on requests


0.13.1 (2015-09-11)
-------------------

- add requests to requirements

0.13.0 (2015-09-10)
-------------------

- switch from httplib to requests
- tests and testing improvements (tox, run in parallel)
- package-level imports and method docs for a better 
  interpreter experience
- documentation site (http://pyonep.readthedocs.org)

0.12.4 (2015-09-03)
-------------------

- add move command

0.12.3 (2015-08-30)
-------------------

- keep consistent ID numbering in RPC calls, again
  for testability

0.12.2 (2015-08-30)
-------------------

- use non-random IDs in RPC calls, for testability

0.12.1 (2015-08-30)
-------------------

- fix exception when testing with VCR.py

0.12.0 (2015-08-14)
-------------------

- use https by default

0.11.3 (2015-07-14)
-------------------

- use RID rather than sharecode by default, for backward compatibility.

0.11.2 (2015-07-01)
-------------------

- add manage_by_sharecode boolean to indicate whether sharecode or RID is 
  used with create model
- fix provisioning example to use sharecode rather than RID

0.11.1 (2015-04-03)
-------------------

- add support for wait command

0.11.0 (2015-02-26)
-------------------

- (breaking change) Undoes the breaking change to listing() in 0.10.0. All 
  old code will continue to call deprecated listing API. New code should 
  pass `options={}` and `rid={'alias': ''}`. This only affects anyone who 
  used 0.10.0.

0.10.0 (2015-02-19)
-------------------

- (breaking change) add rid to listing parameters. Pass {'alias': ''}
  to match previous behavior.

0.9.8 (2015-01-29)
------------------

- add protected parameter for content_create


0.9.7 (2014-12-18)
------------------

- set __repr__ for ProvisionException, too
- support passing entire auth dict in place of CIK

0.9.6 (2014-11-16)
------------------

- sensible output when printing ProvisionException

0.9.5 (2014-11-16)
------------------

- turn off response body encoding for non utf-8 responses
  (e.g. for model content)

0.9.4 (2014-11-15)
------------------

- fix urlencode for python3

0.9.3 (2014-11-15)
------------------

- fix timeout and escape body for curl output

0.9.2 (2014-11-15)
------------------

- support logging requests in curl format

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
