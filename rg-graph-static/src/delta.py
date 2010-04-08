#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf

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

    
if "-target" in sys.argv:
    target = int(sys.argv[sys.argv.index('-target')+1])
else:
    target = model.target

if "-debug" in sys.argv:
    debug = True
else:
    debug = False

if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = model.GraphList()

    
eps = sympy.var('eps')

#print phi3.namec
for n in range(1,target+1):
    for file in g_list:
        G = model.LoadGraph(file) 
        G.DefineNodes({})
        G.WorkDir()
        rggrf.utils.print_debug("---: %s %s" %(file,G.NLoops()), debug)
        if G.NLoops()==n:
            rggrf.utils.print_debug("calc: %s"%file, debug)
            G.GenerateNickel()
            G.LoadResults('eps')
            G.FindSubgraphs()
            D = rggrf.roperation.Delta(G)
            G.__dict__["delta_gamma"] = rggrf.utils.SimpleSeries(D.Calculate('eps'),eps,0,target-G.NLoops())
    #print G.__dict__["r1_dot_gamma"]
    #print G.__dict__["delta_gamma"]
    
            G.__dict__["r1_gamma"] = rggrf.utils.SimpleSeries(-(G.r1_dot_gamma + G.delta_gamma)/G.NLoops()/eps*2, eps, 0, target-G.NLoops()-1)
    
            G.SaveResults(["r1_gamma","delta_gamma"])

