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
    G.Save(overwrite=True)
    
    
#G=G_list[0]
#for idx in G.__dict__:
#    print idx, G.__dict__[idx].__class__.__name__ , G.__dict__[idx]
    
#print G.__dict__['lines'][1]
#lines = {}
#map(lambda k,v: lines.update({k: str(v)}),G.lines.keys(),G.lines.values())
#print lines
#print G._ToDict() 
#
#G = rggrf.Graph(phi3)
#G.LoadLinesFromFile(filename)
#G.DefineNodes({})
#G.GenerateNickel()
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
#print G.sym_coeff

    