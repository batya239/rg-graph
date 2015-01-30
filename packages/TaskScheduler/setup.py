#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='TaskScheduler',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['task_scheduler'],
    license='LICENSE.txt',
    description='Task Scheduler',
    long_description=open('README.txt').read(),
#    requires=['GraphState (>= 0.0.3), Graphine (>= 0.0.1), RgGraphUtil(>= 0.0.1)', sympy]
)
