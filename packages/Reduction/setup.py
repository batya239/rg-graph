#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup
import subprocess
import os

try:
    revision = subprocess.Popen("hg id -i", shell=True, stdout=subprocess.PIPE).stdout.read()[:-1]
    revision_file_name = os.path.join(os.curdir, "reduction", "revision.py")
    with open(revision_file_name, "w+") as f:
        f.write("REVISION = \"%s\"" % revision)
except :
    revision_file_name = None

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

if revision_file_name is not None:
    os.remove(revision_file_name)
