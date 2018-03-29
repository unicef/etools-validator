# -*- coding: utf-8 -*-

import os
import codecs

from setuptools import setup, find_packages

VERSION = __import__('validator').get_version()
HERE = os.path.dirname(__file__)


def read(*files):
    content = ''
    for f in files:
        content += codecs.open(os.path.join(HERE, f), 'r').read()
    return content


setup(
    name='validator',
    url='https://github.com/unicef/validator',
    author='UNICEF',
    author_email='developers@unicef.org',
    description='Django rest framework validation enhancement',
    version=VERSION,
    long_description=read('README.rst'),
    platforms=['any'],
    license='MIT License',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.rst'],
        'validator': ['validator/*'],
    },
    install_requires=read("requirements/base.txt"),
)
