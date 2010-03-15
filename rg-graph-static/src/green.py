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

g_list = phi3.GraphList()
    
eps = sympy.var('eps')
g = sympy.var('g')

greens = dict()
#print phi3.name
for file in g_list:
        print "--- %s"%file,
        G = rggrf.Graph(phi3)
        G.Load(str_nickel=file)
        G.DefineNodes({})
        G.GenerateNickel()
        G.LoadResults('eps')
        if len(G.green)>0 and G.green in greens:
            greens[G.green] = greens[G.green] + G.sym_coeff * G.r1_gamma * g**G.Nloops()
        else:
            greens[G.green] = G.sym_coeff * G.r1_gamma * g**G.Nloops()  
            
            
print greens

