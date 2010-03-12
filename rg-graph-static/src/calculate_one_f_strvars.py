#!/usr/bin/python
# -*- coding:utf8
import sys
import rggraph_static as rggrf


if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

from phi3 import *


print phi3.name

G = rggrf.Graph(phi3)
G.Load()

G.SaveAsPNG("graph.png")
G.GenerateNickel()
base_name = "fstrvars_%s"%str(G.nickel)
TARGET = 4
NLOOPS = len(G.internal_lines) - len(G.internal_nodes) + 1
print "NLOOPS = " , NLOOPS
n_epsilon_series = TARGET - NLOOPS
NPOINTS = 10000
NTHREADS = 2 
SPACE_DIM = 6.
prepared_eqs = []
for idxL in G.internal_lines:
    print "======= %s ======="%idxL
    cur_G = G.Clone()
    cur_G.lines[idxL].dots[1] = 1
    cur_G.DefineNodes()
    cur_G.FindSubgraphs()
    cur_r1 = rggrf.roperation.R1(cur_G)
    cur_r1.SaveAsPNG("test.png")

    if len(G.external_lines) == 2:
        K2res = K2(cur_r1)
        for idxK2 in range(len(K2res)):
            k2term = K2res[idxK2]  
            s_prep =   ExpandScalarProdsAndPrepareFactorized(k2term)
            print "---------dm_%s_p%s --------- " %(idxL,idxK2)
            sys.stdout.flush()
            prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, simplify=True))
   
    elif len(G.external_lines) == 3:
        K0res = K0(cur_r1) 
        s_prep =   ExpandScalarProdsAndPrepareFactorized(K0res)
        prepared_eqs.append(rggrf.integration.PrepareFactorizedStrVars(s_prep, SPACE_DIM, simplify=True))      
        
    sys.stdout.flush()
      
prog_names = rggrf.integration.GenerateMCCodeForGraphStrVars(base_name, prepared_eqs,SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS) 

t_res = rggrf.integration.CalculateEpsilonSeries(prog_names, build=True)
(G.r1_dot_gamma, G.r1_dot_gamma_err) = ResultWithSd(t_res, NLOOPS, n_epsilon_series)

print G.r1_dot_gamma
G.npoints = NPOINTS 
G.SaveResults()

print "симметрийный коэффициент: %s" %(G.sym_coeff)

print "With Sd: %s" %G.r1_dot_gamma

print "Old Notation: %s" % ResultOldNotation(t_res)
#for idx in prog_names:
#    res = rggrf.integration.ExecMCCode(idx)
    