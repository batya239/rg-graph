#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf


from phi3 import *
    
if "-target" in sys.argv:
    target = int(sys.argv[sys.argv.index('-target')+1])
else:
    target = phi3.target

if "-debug" in sys.argv:
    debug = True
else:
    debug = False

if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = phi3.GraphList()

    
eps = sympy.var('eps')

#print phi3.namec
for n in range(1,target+1):
    for file in g_list:
         
        G = rggrf.Graph(phi3)
        G.Load(str_nickel=file)
        G.DefineNodes({})
        rggrf.utils.print_debug("---: %s %s" %(file,G.NLoops()), debug)
        if G.NLoops()==n:
            rggrf.utils.print_debug("calc: %s"%file, debug)
            G.GenerateNickel()
            G.LoadResults('eps')
            G.FindSubgraphs()
            D = rggrf.roperation.Delta(G)
            G.__dict__["delta_gamma"] = rggrf.utils.SimpleSeries(D.Calculate('eps'),eps,0,phi3.target-G.NLoops())
    #print G.__dict__["r1_dot_gamma"]
    #print G.__dict__["delta_gamma"]
    
            G.__dict__["r1_gamma"] = rggrf.utils.SimpleSeries(-(G.r1_dot_gamma + G.delta_gamma)/G.NLoops()/eps*2, eps, 0, phi3.target-G.NLoops()-1)
    
            G.SaveResults(["r1_gamma","delta_gamma"])

