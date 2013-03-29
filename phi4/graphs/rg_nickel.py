#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys
import sympy
import graphine
import graph_state


def internalEdges(graph):
    res = list()
    for edge in graph.allEdges():
        if graph.externalVertex not in edge.nodes:
            res.append(edge)
    return res


def symmetryCoefficient(graph):
    edges = graph.allEdges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = sympy.factorial(len(graph.edges(graph.externalVertex))) / len(graph.toGraphState().sortings)

    for idxE in unique_edges:
        C = C / sympy.factorial(unique_edges[idxE])
    return C


g = sympy.var('g')

fileName = sys.argv[1]

nLoops = int(sys.argv[2])

r1op = eval(open(fileName).read())

Z2 = 1
Z3 = 1

for nickel in r1op:
    graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % nickel))
    graphLoopCount = graph.calculateLoopsCount()
    if graphLoopCount > nLoops:
        continue
    if len(graph.edges(graph.externalVertex)) == 2:
        Z2 -= (-2 * g / 3) ** graphLoopCount * r1op[nickel] * symmetryCoefficient(graph)
    elif len(graph.edges(graph.externalVertex)) == 4:
        Z3 -= (-2 * g / 3) ** graphLoopCount * r1op[nickel] * symmetryCoefficient(graph)
    else:
        raise ValueError("invalid ext legs count: %s, %s" % (graphLoopCount, nickel))

print "Z2 = ", Z2

print "Z3 = ", Z3

Zg = (Z3 / Z2 ** 2).series(g, 0, nLoops + 1).removeO()

print "Zg = ", Zg

print

beta = (-2 * g / (1 + g * sympy.ln(Zg).diff(g))).series(g, 0, nLoops + 2).removeO()

print "beta/2 = ", beta / 2

eta = (beta * sympy.ln(Z2).diff(g)).series(g, 0, nLoops + 1).removeO()

print "eta =", eta
