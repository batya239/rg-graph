#!/usr/bin/python
# -*- coding:utf8

from sympy import *
import rggraph_static as rggrf





from phi3 import *


print phi3.name

G = rggrf.Graph(phi3)
G.Load()
G.GenerateNickel()
G.FindSubgraphs()
print G.nickel

moments = rggrf.moments.Generate(G)
G._UpdateMoments(moments)

G.SaveAsPNG("graph.png")
G.Save(overwrite=True)

#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
#print G.sym_coeff

    