#!/usr/bin/python
# -*- coding:utf8

from sympy import *
import rggraph_static as rggrf





from phi3 import *

if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = phi3.GraphList()
    
if "-debug" in sys.argv:
    debug = True
else:
    debug = False

if "-overwrite" in sys.argv:
    overwrite = True
else:
    overwrite = False
#print phi3.name

for file in g_list:
    rggrf.utils.print_debug(file, debug)
    G = rggrf.Graph(phi3)
    G.Load(file)
    G.GenerateNickel()
    G.FindSubgraphs()
    G.WorkDir()
#print G.nickel

    moments = rggrf.moments.Generate(G)
    G._UpdateMoments(moments)


    G.Save(overwrite=overwrite)
    G.SaveAsPNG("graph.png")

#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
#print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
#print G.sym_coeff

    