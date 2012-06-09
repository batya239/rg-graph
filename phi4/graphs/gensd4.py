#!/usr/bin/python
# -*- coding: utf8

import sys
from dummy_model import _phi4

from graphs import Graph

phi4=_phi4("dummy")

from sd4 import Prepare, print_tree, save_sd
try:
    g1=Graph(sys.argv[1])
except:
   g1=Graph("ee12-e22-e-")
#   g1=Graph("ee12-223-3-ee-")
#   g1=Graph("e123-e34-e34-4-e-")
#   g1=Graph("e12-34-56-56-57-7-e-")
#   g1=Graph("e111-e-")
#   g1=Graph("e12-23-3-e-")
#   g1=Graph("e123-e23-e3-e-")
#   g1=Graph('e123-e24-34-e4-e-')
name=str(g1.GenerateNickel())
print name,  g1.sym_coef()

Prepare(g1,phi4)

#print g1._sectors
#print len(g1._sectors)

print "=========="
#for tree in g1._sectors:
#    print_tree(tree)

save_sd(name, g1, phi4)

#print "=========="
#ss=list(set(g1._sectors))
#print len(ss)
#for sector in ss:
#    print sector
