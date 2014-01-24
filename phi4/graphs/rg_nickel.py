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
    graph = graphine.Graph(graph_state.GraphState.fromStrOldStyle("%s::" % nickel))
    graphLoopCount = graph.getLoopsCount()
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

tau = sympy.var('tau')

beta1 = (beta / g / 2 + 1).expand()

print beta1

gStar = 0
for i in range(1, nLoops):
    gStar = (tau - (beta1 - g).series(g, 0, i + 1).removeO().subs(g, gStar)).series(tau, 0, i + 1).removeO()

print "gStar = ", gStar
gStarS = tau + 0.716173621 * tau**2 + 0.095042867 * tau**3 + 0.086080396 * tau ** 4 - 0.204139 * tau ** 5
print "gStarS = ", gStarS

etaStar = eta.subs(g, gStar).series(tau, 0, nLoops + 1)

print "etaStar = ", etaStar

etaStarGS = eta.subs(g, gStarS).series(tau, 0, nLoops + 1)

print "etaStarGS = ", etaStarGS

