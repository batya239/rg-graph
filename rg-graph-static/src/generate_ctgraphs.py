#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf


from phi3 import *



eps = sympy.var('eps')

G = rggrf.Graph(phi3)
G.Load()
G.DefineNodes({})
G.GenerateNickel()
G.FindSubgraphs()
D = rggrf.roperation.Delta(G)

for term  in D.terms:
    G1 = rggrf.Graph(phi3)
    G2 = rggrf.Graph(phi3)
#    print term.ct_graph
#    print term.subgraph
    try:
        term.ct_graph.GenerateNickel()
#        print term.ct_graph.nickel
        G1.Load(str(term.ct_graph.nickel))
#        print G1
    except:
        G1=term.ct_graph.Clone()
        moments = rggrf.moments.Generate(G1)
        G1._UpdateMoments(moments)
        G1.Save()
        print "Saved %s" %G1.nickel
        
    try:    
        term.subgraph.GenerateNickel()
#        print term.subgraph.nickel
        G2.Load(str(term.subgraph.nickel))
    except:
        G2=term.ct_graph.Clone()
        moments = rggrf.moments.Generate(G1)
        G2._UpdateMoments(moments)
        G2.Save()
        print "Saved %s" %G2.nickel

