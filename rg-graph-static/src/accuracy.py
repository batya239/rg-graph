#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf
import os
import re as regex


from phi3 import *
if "-accuracy" in sys.argv:
    accuracy = float(sys.argv[sys.argv.index('-accuracy')+1])
else:
    accuracy = 0.001
    
eps = sympy.var('eps')

#print phi3.name
for file in phi3.GraphList():
        G = rggrf.Graph(phi3)
        G.Load(str_nickel=file)
        G.DefineNodes({})
        G.GenerateNickel()
        G.LoadResults('eps')
        if "r1_dot_gamma_err" in G.__dict__:
            OK=True
            for i in G.r1_dot_gamma_err:
                if abs(G.r1_dot_gamma_err[i])>accuracy:
                    OK=False
 
            if not OK:
                print G.nickel