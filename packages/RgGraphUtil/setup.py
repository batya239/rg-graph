#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='RgGraphUtil',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['rggraphutil', 'rggraphutil.test', 'rggraphutil.env'],
    url='http://pypi.python.org/pypi/RgGraphUtil/',
    license='LICENSE.txt',
    description='Common utils',
    long_description=open('README.txt').read()
)