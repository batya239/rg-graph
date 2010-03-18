#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf

model =None
def usage(progname):
    return "%s -model phi3R [-target N] [-debug]"

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

g_list = model.GraphList()
    
eps = sympy.var('eps')
g = sympy.var('g')

greens = dict()
#print phi3.name
max_nloop = 0
for file in g_list:
        rggrf.utils.print_debug("---: %s"%file, debug)
        G = rggrf.Graph(model)
        G.Load(str_nickel=file)
        G.DefineNodes({})
        G.GenerateNickel()
        G.LoadResults('eps')
        if len(G.green)>0 and G.green in greens:
            rggrf.utils.print_debug("-----------------------: %s %s %s %s"%(G.green,G.sym_coeff, G.r1_gamma, g**G.NLoops()), debug)
            greens[G.green] = greens[G.green] + G.sym_coeff * G.r1_gamma * g**G.NLoops()
        else:
            greens[G.green] = G.sym_coeff * G.r1_gamma * g**G.NLoops()
        if max_nloop < G.NLoops():
            max_nloop = G.NLoops()  
            
            
for green in greens:
    cur_series=rggrf.utils.SimpleSeries(greens[green], g, 0, max_nloop)
    print "%s : %s"%(green,cur_series) 

