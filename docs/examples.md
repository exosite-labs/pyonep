Examples
========

Here are some examples of how to use pyonep. For more detailed documentation of the Exosite
APIs, you might want to check out [Exosite's RPC API documentation](https://github.com/exosite/docs/tree/master/rpc)
and [Exosite's Provisioning/Device Management API documentation](https://github.com/exosite/docs/tree/master/provision).

Examples are located in [examples/](examples). To run them, first modify them with your
device information.

* [read_write_direct.py](https://github.com/exosite-labs/pyonep/blob/master/examples/read_write_direct.py) - writes to a resource and then reads back
* [get_info.py](https://github.com/exosite-labs/pyonep/blob/master/examples/get_info.py) - gets information about a client, and demonstrates error handling
* [mult_cmd.py](https://github.com/exosite-labs/pyonep/blob/master/examples/mult_cmd.py) - uses the onep module to send
* [read_write_buffered.py](https://github.com/exosite-labs/pyonep/blob/master/examples/read_write_buffered.py) - demonstrates use of the datastore module
* [provisioning.py](https://github.com/exosite-labs/pyonep/blob/master/examples/provisioning.py) - demonstrates use of the provisioning API

Note that to run the examples without installing the pyonep package, the
example script must be located in the root folder (with `./pyonep` as a
sub-folder).

For a Python example that fully exercises the RPC interface using the pyonep
library, see the Exosite command line interface, [exoline](http://github.com/exosite/exoline).
