#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='PolynomialTools',
    version='0.0.3',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['polynomial'],
    url='http://pypi.python.org/pypi/PolynomialTools/',
    license='LICENSE.txt',
    description='Polynomial stuff for SD',
    long_description=open('README.txt').read(),
    requires=['RgGraphUtil (>= 0.0.1)']
)
