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
                if int(i) <= target - G.NLoops():
                    if abs(G.r1_dot_gamma_err[i][0])>=absolute:
                        OK=False
                    elif abs(G.r1_dot_gamma_err[i][1])>=relative:
                        OK=False
 
            if not OK:
                print G.nickel
        else:
            raise Exception, 'Please calculate graph %s ' %G.nickel