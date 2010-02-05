#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
import pydot

print dir(rggrf)
print dir(rggrf.Model)

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

var('p tau p1')

phi3=rggrf.Model("phi3")
phi3.AddLineType(1, propagator = 1/(p*p+tau), directed = 0)

phi3.AddNodeType(0,Lines = [],Factor = 1,Graphviz = "color=\"red\"")  #External Node
phi3.AddNodeType(1,Lines = [1, 1, 1], Factor = 1)
phi3.AddNodeType(2,Lines = [1, 1], Factor = p1 * p1)

phi3.AddSubGraphType(1, Lines = [1, 1])
phi3.AddSubGraphType(2, Lines = [1, 1, 1])

print phi3

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.DefineNodes({})

for idxN in G.Nodes:
    print "idxN=",idxN, "type=", G.Nodes[idxN].Type, "Lines=",G.Nodes[idxN].Lines
for idxL in G.Lines:
    print "idxL=",idxL, "type=", G.Lines[idxL].Type, "In=",G.Lines[idxL].In, "Out=",G.Lines[idxL].Out , "Moment=",G.Lines[idxL].Momenta
    
G.SaveAsPNG("graph.png") 
print G.ExternalLines
print G.InternalLines
print

print G
print "subgraphs"
n=1
for i in rggrf.subgraph.Find(G, phi3.SubGraphTypes):
    print "sub %s" %n
    print i
#    print rggrf.visualization.Graph2dot(i)
    i.SaveAsPNG("sub%s.png" %n)
    n=n+1
    