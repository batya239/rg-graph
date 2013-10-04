#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys

import graphine
import graphine.graph_operations


def isGraph1Irreducible(graph):
    return graphine.graph_operations.isGraph1Irreducible(graph.allEdges(), graph, graph.allEdges())

VacuumLoopName = sys.argv[1]

vl = graphine.Graph.fromStr(VacuumLoopName)

print vl


for vertex in vl.vertexes():
    graph = vl.deleteVertex(vertex, transformEdgesToExternal=True)
    if isGraph1Irreducible(graph):
        print vertex, graph