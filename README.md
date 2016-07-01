About pyonep
============

The pyonep package is an API library with Python bindings to the 
following Exosite One Platform APIs:

* [RPC API](https://github.com/exosite/docs/tree/master/rpc)
* [Provisioning/Device Management API](https://github.com/exosite/docs/tree/master/provision)

Check out our docs on [Read The Docs](https://pyonep.readthedocs.org/).


__Warning__: version 0.13.4 requires changes to applications that used 
earlier versions of pyonep. See below for information about 
[migrating your applications from 0.12.x to 0.13.4](#migrating-to-0134)

Note that this library does not support the HTTP Data Interface. See
below for more information.

Supports Python 2.6 through 3.3.

License is BSD, Copyright 2016, Exosite LLC (see LICENSE file)


Installation
------------

For installation instructions, check out [Read The Docs](https://pyonep.readthedocs.org/en/latest/install.html).


Tests
-----

Before testing, you'll need the test requirements.

```bash
$ pip install -r test/requirements.txt
...
```

Run all the tests in your current Python version.

```bash
$ ./test.sh --processes=2 --process-timeout=40
```

Run all the tests in every supported Python version:

```bash
$ time ./test.sh full --processes=2 --process-timeout=40
Starting test for py26
Starting test for py27
Starting test for py32
Starting test for py33
Starting test for py34
Waiting for tests to finish
All tests passed. Congratulations! :)

real0m29.966s
user0m31.221s
sys0m5.684s
```

To run a single test in your current Python version:

```bash
$ nosetests -q -s test/test_rpc.py:TestRPC.test_move
----------------------------------------------------------------------
Ran 1 test in 35.734s

OK
```

Occasionally this error happens. Deleting .tox directories helps.

```bash
...
  File "/Users/danw/prj/exosite/pyonep/.tox-py26/py26/lib/python2.6/site-packages/coverage/data.py", line 202, in combine_parallel_data
      os.remove(full_path)
      OSError: [Errno 2] No such file or directory: '/Users/danw/prj/exosite/pyonep/.coverage.civet.51448.095287'
...
$ rm -rf .tox-py*
```


Migrating to 0.13.4
-------------------

Version 0.13.4 includes two breaking changes:

- datastore.py is removed
- `rid` parameter is renamed to `resource`



Migrating to 0.8.0
------------------

Version 0.8.0 includes some breaking changes to provision module API to provide more consistent return values and error information. To migrate an existing application to pyonep 0.8.0 you will need to make a few changes to the way provision methods are called.

- Previously, methods in provision module either returned a.) `True` (success) or `False` (failure) or b.) `<response body string>` (success) or `None` (failure). HTTP response details (e.g. status code) were not available to the caller without turning on logging and parsing stdout. With 0.8.0 all methods return a `ProvisionResponse` object with the following properties:

    - `ProvisionResponse.body` is the response body, a string. The contents of this depend on the specific call, and may be of length 0. See [provision API documentation](https://github.com/exosite/docs/tree/master/provision) for details.
    - `ProvisionResponse.status` is the HTTP status code
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
import sys
import httplib
import pyonep

# the leading 'http://' is now optional but should be omitted
provision = pyonep.Provision('m2.exosite.com', manage_by_cik=False)

try:
    # create a model
    response = provision.model_create(vendortoken, model, clonerid, aliases=False)
    if not response.isok:
        print('Error in model_create: {0} {1}'.format(response.status(), response.reason()))

    # list models
    response = provision.model_list(vendortoken)
    if response.isok:
        print(response.body)
    else:
        print('Error in model_list: {0} {1}'.format(response.status(), response.reason()))
except httplib.HTTPException:
    ex = sys.exc_info()[1]
    print('HTTPException: {0}'.format(ex))
```

You can also ask the provision module to raise an exception for HTTP statuses of 400 and above by passing `raise_api_exceptions=True` to the `Provision` constructore. This can consolidate code that handles API errors for a large number of provision calls. See the [provisioning example](examples/provisioning.py) to see how to do this.
