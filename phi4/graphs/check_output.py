#!/usr/bin/python

import sys
import os
import fnmatch
import re
from graphs import Graph

import cluster.tools as tools
from dummy_model import _phi4

method = sys.argv[1]
accuracy = float(sys.argv[2])
#name = sys.argv[2]
phi4=_phi4('dummy')
try:
    exec('from %s import normalize'%method)
except ImportError:
    normalize=lambda x, y: y

for dir in os.listdir('.'):
   if re.match('^e.*-$', dir):
       g=Graph(dir)
       try:
          tools.print_bad(tools.find_bestresult(dir),accuracy, normalize, g)
       except:
          print dir, "Error"
