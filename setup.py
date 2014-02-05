from distutils.core import setup

from pyonep import __version__ as version

try:
    import json
except ImportError:
    try:
        import simplejson
        print("###### running python version earlier than 2.6 but simplejson is present")
    except ImportError:

        print("######")
        print("###### pyonep requires python-simplejson for use with Python 2.5")
        print("###### It may be found here: https://pypi.python.org/pypi/simplejson/")
        print("######")

setup(name='pyonep',
      version=version,
      url='http://github.com/exosite-labs/pyonep',
      author='Exosite',
      author_email='labs@exosite.com',
      description='Python bindings for Exosite API over HTTP JSON RPC.',
      long_description=open('README.md').read() + '\n\n' +
                       open('HISTORY.md').read(),
      packages=['pyonep'],
      package_dir={'pyonep': 'pyonep'},
      keywords=['exosite', 'onep', 'one platform', 'm2m']
      )
