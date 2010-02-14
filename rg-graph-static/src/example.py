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

var('p tau p1')

def propagator(**kwargs):
    var('tau')
    momenta = kwargs["momenta"]
    return 1 / (momenta.Squared() + tau)

def external_node_factor(**kwargs):
    return 1

def triple_node_factor(**kwargs):
    return 1

def double_node_factor(**kwargs):
    squared_momenta = kwargs["momenta0"].Squared()
    return squared_momenta

def dot_action(**kwargs):
    var('tau')
    propagator=kwargs["propagator"]
    return propagator.diff(tau)

def K(**kwargs):
    pass

            

phi3=rggrf.Model("phi3")
phi3.AddLineType(1, propagator=propagator, directed=0)

phi3.AddNodeType(0, Lines=[], Factor=external_node_factor,
                 gv={"color": "red"})  #External Node
phi3.AddNodeType(1, Lines=[1, 1, 1], Factor=triple_node_factor)
phi3.AddNodeType(2, Lines=[1, 1], Factor=double_node_factor) # nodes from Sigma subgraphs
phi3.AddNodeType(3, Lines=[1, 1, 1], Factor=K, gv={"color": "blue"})
phi3.AddNodeType(4, Lines=[1, 1], Factor=K, gv={"color": "blue"})


phi3.AddSubGraphType(1, Lines=[1, 1, 1], dim=0, K_nodetypeR1=3)
phi3.AddSubGraphType(2, Lines=[1, 1], dim=2, K_nodetypeR1=4)

phi3.AddDotType(1, dim=2, action=dot_action, gv={"penwidth":"3"})
print phi3.line_types[1]["propagator"](momenta=rggrf.Momenta(string="+p-q1"))

print phi3

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.lines[6].dots[1] = 1
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
    