#!/usr/bin/python

import sys
import re

lines = open(sys.argv[1]).readlines()
term = False
res = dict()
for line in lines:
   reg=re.search("ng\sMCTF_2_.*_(\d+)_e0",line)
   if not term and reg:
      n_term= int(reg.groups()[0])
      term = True
   reg=re.search("res = (.*), err = (.*), delta = (.*)",line)
   if term and reg:
      res[n_term] = ( reg.groups()[0], reg.groups()[1], reg.groups()[2])
      term = False

keys =  res.keys()
keys.sort()
for i in keys:
   (a,b,c) = res[i]
   print "%s\t%s\t%s"%(i,a,b)
