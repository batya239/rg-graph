#!/usr/bin/python
# -*- coding:utf8

from sympy import *
import rggraph_static as rggrf
print dir(rggrf)
print dir(rggrf.Model)
var('p tau p1')

phi3=rggrf.Model("phi3")
phi3.addLineType(1,propagator=1/(p*p+tau),directed=0)

phi3.addNodeType(0,Lines=[],Factor=1)  #External Node
phi3.addNodeType(1,Lines=[1,1,1],Factor=1)
phi3.addNodeType(2,Lines=[1,1],Factor=p1*p1)

print phi3

G=rggrf.Graph(phi3)
(moment,Lines)=eval(open("moment").read())
print moment
print Lines
for idxL in Lines:
    tmpLine=rggrf.Line(1,Lines[idxL][0],Lines[idxL][1],moment[idxL])
    G.addLine(idxL,tmpLine)
G.defineNodes({0:0,1:0})

for idxN in G.Nodes:
    print "idxN=",idxN, "type=", G.Nodes[idxN].Type, "Lines=",G.Nodes[idxN].Lines
for idxL in G.Lines:
    print "idxL=",idxL, "type=", G.Lines[idxL].Type, "In=",G.Lines[idxL].In, "Out=",G.Lines[idxL].Out , "Moment=",G.Lines[idxL].Momenta
