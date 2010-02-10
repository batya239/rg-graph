#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
import pydot

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

var('p tau p1 K')

phi3=rggrf.Model("phi3")
phi3.AddLineType(1, propagator = 1/(p*p+tau), directed = 0)

phi3.AddNodeType(0, Lines = [],Factor = 1,Graphviz = "color=\"red\"",gv = {"color":"red"})  #External Node
phi3.AddNodeType(1, Lines = [1, 1, 1], Factor = 1)
phi3.AddNodeType(2, Lines = [1, 1], Factor = p1 * p1) # nodes from Sigma subgraphs
phi3.AddNodeType(3, Lines = [1, 1 , 1], Factor = K , gv = {"color":"blue"})
phi3.AddNodeType(4, Lines = [1, 1], Factor = K , gv = {"color":"blue"})


phi3.AddSubGraphType(1, Lines = [1, 1, 1], dim = 0, K_nodetypeR1 = 3)
phi3.AddSubGraphType(2, Lines = [1, 1], dim = 2, K_nodetypeR1 = 4)

print phi3

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
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
#print "subgraphs"

G.FindSubgraphs()

#for i in range(len(G.subgraphs)):
#    print "sub %s" %i
#    print G.subgraphs[i]
    
r1=rggrf.roperation.R1(G)
#print "R1(G)"
#for i in range(len(r1.terms)):
#    print "term %s:"  %i
#    print r1.terms[i].CTGraph
#    print r1.terms[i].SubgraphMap    
#    print "\t term subgraphs:"
#    for j in r1.terms[i].subgraphs:
#        print "\t %s" %j
        
G.GenerateNickel()
print G.nickel
G.SaveAsPNG("graph_and_subgraphs.png")
r1.SaveAsPNG("R1.png")
    