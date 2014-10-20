#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='RStar',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['rstar', 'rstar.test'],
    url='http://pypi.python.org/pypi/RStar/',
    license='LICENSE.txt',
    description='Calculating diagrams using R* operation',
    long_description=open('README.txt').read(),
#    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)', sympy]
)
