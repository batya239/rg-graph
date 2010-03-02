#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf



if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    print "Usage: %s out.grc" %sys.argv[0]
    sys.exit(1)

from phi3 import *


print phi3.name
G_list = rggrf.graph.LoadFromGRC(filename,phi3)
for G in G_list:
    G.GenerateNickel()
    print G.nickel, G.sym_coeff
#
#G = rggrf.Graph(phi3)
#G.LoadLinesFromFile(filename)
#G.DefineNodes({})
#G.GenerateNickel()
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
#print G.sym_coeff

    