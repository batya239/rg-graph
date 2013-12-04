#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup
import os.path

setup(
    name='PoleExtractor',
    version='0.0.1',
    author='G. Dovzhenko',
    author_email='dovjenko.g@gmail.com',
    packages=['pole_extractor'],
    data_files=[(os.path.expanduser("~") + '/.pole_extractor', ['pole_extractor/integrate.c'])],
    license='LICENSE.txt',
    description='SD and analytical continuation of Feynman Representation.',
    long_description=open('README.txt').read(),
)
