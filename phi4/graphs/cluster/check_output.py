#!/usr/bin/python

import sys
import os
import fnmatch
import re

import tools

accuracy = float(sys.argv[1])
#name = sys.argv[2]

for dir in os.listdir('.'):
   if re.match('e.*-', dir):
       tools.print_bad(tools.find_bestresult(dir),accuracy)
