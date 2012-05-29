#!/usr/bin/python
# -*- coding: utf8

import sys
from dummy_model import _phi4

from graphs import Graph

phi4=_phi4("dummy")

from sd3 import Prepare

#g1=Graph(sys.argv[1])
g1=Graph("ee12-e22-e-")
g1=Graph("ee12-223-3-ee-")
#g1=Graph("e123-e23-e3-e-")
#g1=Graph('e123-e24-34-e4-e-')
name=str(g1.GenerateNickel())
print name

Prepare(g1,phi4)

#print g1._sectors
print len(g1._sectors)

print "=========="
for sector in g1._sectors:
    print sector

print "=========="
for sector in sorted(g1._sectors):
    print sector
