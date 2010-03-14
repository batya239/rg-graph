#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf

from phi3 import *
if "-absolute" in sys.argv:
    absolute = float(sys.argv[sys.argv.index('-absolute')+1])
else:
    absolute = 0.00001

if "-relative" in sys.argv:
    relative = float(sys.argv[sys.argv.index('-relative')+1])
else:
    relative = 0.01
    
if "-target" in sys.argv:
    target = int(sys.argv[sys.argv.index('-target')+1])
else:
    target = phi3.target

if "-graph" in sys.argv:
    g_list = [sys.argv[sys.argv.index('-graph')+1],]
else:
    g_list = phi3.GraphList()
    
eps = sympy.var('eps')

#print phi3.name
for file in g_list:
        #print "--- %s"%file,
        G = rggrf.Graph(phi3)
        G.Load(str_nickel=file)
        G.DefineNodes({})
        G.GenerateNickel()
        G.LoadResults('eps')
        if not G.CheckAccuracy(absolute, relative):
            print file

        