#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='GFunctions',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['gfunctions', 'gfunctions.test'],
    url='http://pypi.python.org/pypi/Graphine/',
    license='LICENSE.txt',
    description='Manipulating on graphs',
    long_description=open('README.txt').read(),
    requires=['GraphState (>= 0.0.3), ']
)