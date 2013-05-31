#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='GFunctions',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['gfunctions', 'gfunctions.test'],
    url='http://pypi.python.org/pypi/GFunctions/',
    license='LICENSE.txt',
    description='Calculationg FD using G-functions',
    long_description=open('README.txt').read(),
#    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)']
)
