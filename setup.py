import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'cryptography',
    'pycoin',
    'blockchain',
    'nvblib',
    ]

dependency_links = [
    'git+ssh://git@github.com:XertroV/nvblib.git',
    'git+ssh://git@github.com:richardkiss/pycoin.git',  # requires new op_return pull #123
]


setup(name='nvb-client',
      version='0.0.1',
      description='nvb-client',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Max Kaye',
      author_email='nvb-client@xk.io',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='nvbclient',
      install_requires=requires,
      dependency_links=dependency_links,
      entry_points="""\
      [paste.app_factory]
      main = nvbclient:main
      [console_scripts]
      initialize_nvb_client_db = nvbclient.scripts.initializedb:main
      """,
      )
