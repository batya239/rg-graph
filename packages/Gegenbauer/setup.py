#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='Gegenbauer',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['gegenbauer', 'gegenbauer.test', 'xspace', 'xspace.test'],
    url='http://pypi.python.org/pypi/Gegenbauer/',
    license='LICENSE.txt',
    description='Calculations on FD using GPXT',
    long_description=open('README.txt').read(),
    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)']
)