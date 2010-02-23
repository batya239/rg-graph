#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
#import pydot
import copy
from rggraph_static.utils import print_time

print_time("start")

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

from phi3 import *


print phi3.name

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.DefineNodes({})
G.SaveAsPNG("graph.png")
G_list = []
R1_list = []
print_time("define nodes")
G.GenerateNickel()
print_time("nickel")
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
    print_time("line %s" %idxL)
    cur_G = G.Clone()
    cur_G.lines[idxL].dots[1] = 1
    cur_G.DefineNodes()
    print_time("define nodes")
    cur_G.FindSubgraphs()
    print_time("Find subgraphs")
    cur_r1 = rggrf.roperation.R1(cur_G)
    print_time("r operation done")
    cur_r1.SaveAsPNG("R1_%s_dm%s.png" %(base_name, idxL))

    if len(G.external_lines) == 2:
        K2res = K2(cur_r1)
        print_time("K2operation done")
        for idxK2 in range(len(K2res)):
            print_time("K2term %s"%idxK2)
            k2term = K2res[idxK2]  
            s_prep =   ExpandScalarProdsAndPrepare(k2term)
            print_time("Expand scalar prod")
            print "---------dm_%s_p%s --------- " %(idxL,idxK2)
#            pretty_print(s_prep)
            (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, SPACE_DIM)
            print_time("Prepare")
#            print "\ng_expr:\n%s\n"%g_expr
            name = "MC_%s_dm%s_p%s" %(base_name, idxL, idxK2)
            prog_names = prog_names + rggrf.integration.GenerateMCCodeForTerm(name, g_expr, g_vars, SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS)
            print_time("GenerateMC")
    
    elif len(G.external_lines) == 3:
        K0res = K0(cur_r1) 
        print_time("K0 operation done")
        s_prep =   ExpandScalarProdsAndPrepare(K0res)
        print_time("Expand scalar prod")
#        pretty_print(s_prep)
        (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, SPACE_DIM)
        print_time("Prepare")
        name = "MC_%s_dm%s_p%s" %(base_name, idxL, 0)
        prog_names = prog_names+rggrf.integration.GenerateMCCodeForTerm(name, g_expr, g_vars, SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS)
        print_time("GenerateMC")
    sys.stdout.flush()
#print prog_names

res = rggrf.integration.CalculateEpsilonSeries(prog_names, build=True)
print res
print "симметрийный коэффициент: %s" %(G.sym_coeff)

print "With Sd: %s" %ResultWithSd(res, NLOOPS, n_epsilon_series)

print "Old Notation: %s" % ResultOldNotation(res)
#for idx in prog_names:
#    res = rggrf.integration.ExecMCCode(idx)
    