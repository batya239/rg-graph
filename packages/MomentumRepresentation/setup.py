#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='MomentumRepresentation',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['momentumrepr', 'momentumrepr.scons', 'momentumrepr.test', 'momentumrepr.ms', 'momentumrepr.ms.scons'],
    package_data={'momentumrepr': ['scons/*.*', 'ms/scons/*.*']},
    license='LICENSE.txt',
    description='Momentum representation for FD',
    long_description=open('README.txt').read(),
#    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)', sympy]
)
