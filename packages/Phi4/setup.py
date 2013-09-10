#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='Phi4',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['gfunctions', 'gfunctions.test', 'mincer_adapter', 'mincer_adapter.test'],
    package_data={'mincer_adapter': ['lib/*.h']},
    url='http://pypi.python.org/pypi/Phi4/',
    license='LICENSE.txt',
    description='Calculating phi4',
    long_description=open('README.txt').read(),
#    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)', sympy]
)
