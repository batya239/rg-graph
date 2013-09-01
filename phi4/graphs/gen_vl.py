#!/usr/bin/python

import topology
import sys
import graphine
import graphine.graph_operations


def isGraphVertexIrreducible(graph):
    return graphine.graph_operations.isGraphVertexIrreducible(graph.allEdges(), graph, None)



valence = int(sys.argv[1])
nvertex = int(sys.argv[2])

topologies = [t for t in topology.GetTopologies({valence: nvertex})]

for t in topologies:
    if isGraphVertexIrreducible(graphine.Graph.fromStr(t)):
        print t

