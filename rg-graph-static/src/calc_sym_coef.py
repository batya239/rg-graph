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
    
eps = sympy.var('eps')



for file in g_list:
        #print "--- %s"%file,
        G = rggrf.Graph(phi3)
        G.Load(str_nickel=file)
        G.DefineNodes({})
        G.GenerateNickel()
        print G.sym_coeff

    

    