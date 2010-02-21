#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
#import pydot
import copy

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

from phi3 import *


print phi3

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.DefineNodes({})
G.SaveAsPNG("graph.png")
G_list = []
R1_list = []
G.GenerateNickel()
base_name = str(G.nickel)
TARGET = 4
NLOOPS = len(G.internal_lines) - len(G.internal_nodes) + 1
print "NLOOPS = " , NLOOPS
#print len(G.internal_lines) , len(G.internal_nodes)
n_epsilon_series = TARGET - NLOOPS
NPOINTS = 10000
NTHREADS = 2 
SPACE_DIM = 6.
prog_names = []
for idxL in G.internal_lines:
    cur_G = G.Clone()
    cur_G.lines[idxL].dots[1] = 1
    cur_G.DefineNodes()
    cur_G.FindSubgraphs()
    cur_r1 = rggrf.roperation.R1(cur_G)
    cur_r1.SaveAsPNG("R1_%s_dm%s.png" %(base_name, idxL))

    if len(G.external_lines) == 2:
        K2res = K2(cur_r1)
        for k2term in K2res:  
            s_prep =   ExpandScalarProdsAndPrepare(k2term)
            (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, SPACE_DIM)
            name = "MC_%s_dm%s_p%s" %(base_name, idxL, K2res.index(k2term))
            prog_names = prog_names + rggrf.integration.GenerateMCCode(name, g_expr, g_vars, SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS)
    
    elif len(G.external_lines) == 3:
        K0res = K0(cur_r1) 
        s_prep =   ExpandScalarProdsAndPrepare(K0res)
        pretty_print(s_prep)
        (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, SPACE_DIM)
        name = "MC_%s_dm%s_p%s" %(base_name, idxL, 0)
        prog_names = prog_names+rggrf.integration.GenerateMCCode(name, g_expr, g_vars, SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS)
        
print prog_names

res = rggrf.integration.CalculateEpsilonSeries(prog_names)
print res
#for idx in prog_names:
#    res = rggrf.integration.ExecMCCode(idx)
    