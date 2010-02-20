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
G.lines[4].dots[1] = 1
G.DefineNodes({})

for idxN in G.nodes:
    print "idxN=",idxN, "type=", G.nodes[idxN].type, "Lines=",G.nodes[idxN].lines
for idxL in G.lines:
    print "idxL=",idxL, "type=", G.lines[idxL].type, "In=",G.lines[idxL].start, "Out=",G.lines[idxL].end , "Moment=",G.lines[idxL].momenta
    
G.SaveAsPNG("graph.png") 
print G.external_lines
print G.internal_lines
print

print G


G.FindSubgraphs()


    
r1 = rggrf.roperation.R1(G)

        
G.GenerateNickel()
print G.nickel
G.SaveAsPNG("graph_and_subgraphs.png")
r1.SaveAsPNG("R1.png")

TARGET = 4
NLOOPS = len(G.internal_lines) - len(G.internal_nodes)
print "NLOOPS = " , NLOOPS
n_epsilon_series = TARGET - NLOOPS
NPOINTS = 10000
NTHREADS = 2 
SPACE_DIM = 6.
prog_names = []
base_name = str(G.nickel)
if len(G.external_lines) == 2:
    K2res = K2(r1)
    for k2term in K2res:  
        s_prep =   ExpandScalarProdsAndPrepare(k2term)
        (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, SPACE_DIM)
        name = "%s_m%s" %(base_name, K2res.index(k2term))
        prog_names = prog_names + rggrf.integration.GenerateMCCode(name, g_expr, g_vars, SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS)

elif len(G.external_lines) == 3:
    K0res = K0(r1) 
    print K0res
    pretty_print(K0res)
    s_prep =   ExpandScalarProdsAndPrepare(K0res)
    pretty_print(s_prep)
    (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, SPACE_DIM)
    name = "%s_m%s" %(base_name, 0)
    prog_names = rggrf.integration.GenerateMCCode(name, g_expr, g_vars, SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS)
print prog_names    