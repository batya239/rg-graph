#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='Graphine',
    version='1.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['graphine', 'graphine.test'],
    url='http://pypi.python.org/pypi/Graphine/',
    license='LICENSE.txt',
    description='Graph manipulation package based on GraphState',
    long_description=open('README.txt').read(),
    requires=['GraphState (>= 1.0.0)']
)
