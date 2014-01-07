#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='Reduction',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['reduction', 'reduction.test'],
    package_data={'reduction': ['loop*/*']},
    url='http://pypi.python.org/pypi/Reduction/',
    license='LICENSE.txt',
    description='FD reduction',
    long_description=open('README.txt').read(),
#    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)', sympy]
)
