#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
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

#print phi3.name
eps = sympy.var('eps')
while len(g_list)>0:
    rggrf.utils.print_debug("len(g_list)=%s"%len(g_list), debug)
    t_list=[]
    for file in g_list:
        rggrf.utils.print_debug(file, debug)
        G = rggrf.Graph(phi3)
        G.Load(file)
        G.DefineNodes({})
        G.GenerateNickel()
        G.FindSubgraphs()
        D = rggrf.roperation.Delta(G)
    
        for term  in D.terms:
            G1 = rggrf.Graph(phi3)
            G2 = rggrf.Graph(phi3)
            try:
                term.ct_graph.GenerateNickel()
    
                G1.Load(str(term.ct_graph.nickel))
    
            except:
                G1=term.ct_graph.Clone()
                moments = rggrf.moments.Generate(G1)
                G1._UpdateMoments(moments)
                G1.Save()
                rggrf.utils.print_debug("found: %s"%G1.nickel, debug)
                t_list.append(str(G1.nickel))
            
            try:    
                term.subgraph.GenerateNickel()
    #        print term.subgraph.nickel
                G2.Load(str(term.subgraph.nickel))
            except:
                G2=term.ct_graph.Clone()
                moments = rggrf.moments.Generate(G1)
                G2._UpdateMoments(moments)
                G2.Save()
                rggrf.utils.print_debug("found: %s"%G2.nickel, debug)
                t_list.append(str(G2.nickel))
                
    g_list = t_list
