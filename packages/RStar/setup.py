#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='RStar',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['rstar'],
    url='',
    license='LICENSE.txt',
    description='RStar',
    long_description=open('README.txt').read(),
    requires=['RgGraphUtil (>= 0.0.1)']
)
