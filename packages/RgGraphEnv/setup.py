#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='RgGraphEnv',
    version='0.0.1',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['rggraphenv', 'rggraphenv.test'],
    url='http://pypi.python.org/pypi/RgGraphEnv/',
    license='LICENSE.txt',
    description='Common environments',
    long_description=open('README.txt').read()
)