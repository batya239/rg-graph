#!/usr/bin/python
# -*- coding: utf8

import graph_state
import sympy
import normed5loop

def symmetryCoefficient(graphstate):
    edges = graphstate.edges
    unique_edges = dict()
    externalLegCount = 0
    for edge in edges:
        if -1 in edge.nodes:
            externalLegCount += 1
        if str(edge) in unique_edges:
            unique_edges[str(edge)] = unique_edges[str(edge)] + 1
        else:
            unique_edges[str(edge)] = 1
    C = sympy.factorial(externalLegCount) / len(graphstate.sortings)
    for idxE in unique_edges:
#        print idxE,unique_edges[idxE]
        C = C / sympy.factorial(unique_edges[idxE])

    return C


diags = eval(open('VacuumLoopsForG4.txt').read())

graphsByNumber = dict()
graphsByNickel = dict()
for (idx, vl, graphs) in diags:
    for graphIdx in graphs:
        if graphIdx in graphsByNumber:
            raise ValueError("graphIdx %s allready exists" % graphIdx)
        graphsByNumber[graphIdx] = graphs[graphIdx]
        if graphs[graphIdx] in graphsByNickel:
            raise ValueError("graph %s allready exists" % graphs[graphIdx])
        graphsByNickel[graphs[graphIdx]] = graphIdx
#print graphsByNickel
#print
#print graphsByNumber


for idx in sorted(graphsByNumber.keys()):
    graphstate = graph_state.GraphState.fromStr(graphsByNumber[idx])

    print idx, graphsByNumber[idx], symmetryCoefficient(graphstate), "\t", normed5loop.MS[graphsByNumber[idx]].expand().series(normed5loop.e,0)