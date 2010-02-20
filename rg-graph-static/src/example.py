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
G.lines[5].dots[1] = 1
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

if len(G.external_lines) == 2:
    tmp = K2(r1)
    print tmp , "\n\n"
    pretty_print(tmp)
    s_prep =   ExpandScalarProdsAndPrepare(tmp[0])
    print "s_prep", s_prep
    (g_expr, g_vars) = rggrf.integration.Prepare(s_prep, 6)
    print "Prepare", g_expr

    
#    s_ginac.set_print_context('c')

    
elif len(G.external_lines) == 3:
    tmp = K0(r1) 
    print tmp , "\n\n"
    pretty_print(tmp)
    