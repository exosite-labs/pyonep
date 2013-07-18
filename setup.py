from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='pyonep',
      version='0.7.0',
      url='http://github.com/dweaver/pyonep',
      author='Exosite',
      author_email='danweaver@exosite.com',
      description='Python bindings for Exosite API over HTTP JSON RPC.',
      long_description = open('README.md').read() + '\n\n' +
                         open('HISTORY.md').read(),
      packages=['pyonep'],
      package_dir={'exoline': 'exoline'},
      keywords=['exosite', 'onep', 'one platform', 'm2m'],
      install_requires=required,
      zip_safe=False,
      )
