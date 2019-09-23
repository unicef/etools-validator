#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import codecs
import os.path
import re
import subprocess
import sys
from codecs import open
from distutils import log
from distutils.errors import DistutilsError

from setuptools import find_packages, setup
from setuptools.command.install import install

ROOT = os.path.realpath(os.path.dirname(__file__))
init = os.path.join(ROOT, 'src', 'etools_validator', '__init__.py')
_version_re = re.compile(r'__version__\s+=\s+(.*)')
_name_re = re.compile(r'NAME\s+=\s+(.*)')

sys.path.insert(0, os.path.join(ROOT, 'src'))

with open(init, 'rb') as f:
    content = f.read().decode('utf-8')
    VERSION = str(ast.literal_eval(_version_re.search(content).group(1)))
    NAME = str(ast.literal_eval(_name_re.search(content).group(1)))


def read(*files):
    content = []
    for f in files:
        content.extend(codecs.open(os.path.join(ROOT, 'src', 'requirements', f), 'r').readlines())
    return "\n".join(filter(lambda l:not l.startswith('-'), content))


class VerifyTagVersion(install):
    """Verify that the git tag matches version"""

    def run(self):
        tag = os.getenv("CIRCLE_TAG")
        if tag != VERSION:
            info = "Git tag: {} does not match the version of this app: {}".format(
                tag,
                VERSION
            )
            sys.exit(info)


setup(name=NAME,
      version=VERSION,
      url='https://github.com/unicef/etools-validator',
      author='UNICEF',
      author_email='dev@unicef.org',
      license="Apache 2 License",
      description='Django package that handles exporting of data',
      long_description=codecs.open('README.rst').read(),
      package_dir={'': 'src'},
      packages=find_packages(where='src'),
      include_package_data=True,
      install_requires=read('install.pip'),
      extras_require={
          'test': read('install.pip', 'testing.pip'),
      },
      platforms=['any'],
      classifiers=[
          'Environment :: Web Environment',
          'Programming Language :: Python :: 3.6',
          'Framework :: Django',
          'Intended Audience :: Developers'],
      scripts=[],
      cmdclass={
          "verify": VerifyTagVersion,
      }
)
