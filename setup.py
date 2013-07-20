from distutils.core import setup

setup(name='pyonep',
      version='0.7.3',
      url='http://github.com/exosite-labs/pyonep',
      author='Exosite',
      author_email='labs@exosite.com',
      description='Python bindings for Exosite API over HTTP JSON RPC.',
      long_description=open('README.md').read() + '\n\n' +
                         open('HISTORY.md').read(),
      packages=['pyonep'],
      package_dir={'exoline': 'exoline'},
      keywords=['exosite', 'onep', 'one platform', 'm2m'],
      )
