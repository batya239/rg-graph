#!/usr/bin/python
# -*- coding:utf8
import sys
import sympy 
import rggraph_static as rggrf


from phi3 import *


#print phi3.name
eps = sympy.var('eps')

G = rggrf.Graph(phi3)
G.Load()
G.DefineNodes({})
G.GenerateNickel()
print G.sym_coeff
G.LoadResults('eps')
G.FindSubgraphs()
D = rggrf.roperation.Delta(G)
G.__dict__["delta_gamma"] = rggrf.utils.SimpleSeries(D.Calculate('eps'),eps,0,phi3.target-G.NLoops())
#print G.__dict__["r1_dot_gamma"]
#print G.__dict__["delta_gamma"]

eps=sympy.var('eps')
G.__dict__["r1_gamma"] = rggrf.utils.SimpleSeries(-(G.r1_dot_gamma + G.delta_gamma)/G.NLoops()/eps*2, eps, 0, phi3.target-G.NLoops()-1)

G.SaveResults()

print G.r1_gamma