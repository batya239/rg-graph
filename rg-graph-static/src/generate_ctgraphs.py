#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy
import rggraph_static as rggrf
model = None

def usage(progname):
    return "%s -model phi3R [-graph str_nickel] [-debug]"

if "-model" in sys.argv:
    model_module = sys.argv[sys.argv.index('-model')+1]
    try:
        exec('from %s import *'%model_module)
    except:
        print "Error while importing model!"
        sys.exit(1)
else:
    print "Usage : %s " %usage(sys.argv[0])
    sys.exit(1)
    
if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = model.GraphList()
    
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
        G = model.LoadGraph(file)
        G.GenerateNickel()
        G.FindSubgraphs()
#        for sub in G.subgraphs:
#            print "sub: %s"%sub.internal_lines
        D = rggrf.roperation.Delta(G)
    
        for term  in D.terms:
            try:
                term.ct_graph.GenerateNickel()
    
                G1=model.LoadGraph(str(term.ct_graph.nickel))
    
            except:
                G1=term.ct_graph
                moments = rggrf.moments.Generate(G1)
                G1._UpdateMoments(moments)
                G1.Save()
                rggrf.utils.print_debug("found: %s"%G1.nickel, debug)
                t_list.append(str(G1.nickel))
            
            try:    
                term.subgraph.GenerateNickel()
    #        print term.subgraph.nickel
                G2 = model.LoadGraph(str(term.subgraph.nickel))
            except:
                G2=term.ct_graph
                moments = rggrf.moments.Generate(G2)
                G2._UpdateMoments(moments)
                G2.Save()
                rggrf.utils.print_debug("found: %s"%G2.nickel, debug)
                t_list.append(str(G2.nickel))
                
    g_list = t_list
