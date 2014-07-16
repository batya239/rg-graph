#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='UncertSeries',
    version='0.0.1',
    author='Kirienko',
    author_email='yury.kirienko@gmail.com',
    packages=['uncertSeries'],
    url='',
    license='LICENSE.txt',
    description='Series with uncertain coefficients',
    long_description=open('README.txt').read(),
    requires=['uncertainties (>= 2.4.0)']
)
