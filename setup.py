
from setuptools import setup

import csp


NAME = "python-csp"
VERSION = csp.__version__
AUTHOR = csp.__author__
DESCRIPTION="Python implementation of Communicating Sequential Processes"


setup(name=NAME,
      description=DESCRIPTION,
      version=VERSION,
      author=AUTHOR,
      packages=["csp"],
      test_suite="csp.tests")
