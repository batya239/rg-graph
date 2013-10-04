#!/usr/bin/python
# -*- coding: utf8
import graph_operations


def graphFilter(qualifier):
    """
    graphFilter should be used as decorator

    @graphFilter
    def myFilter(...):
      ...
    """
    return [qualifier]


def isRelevant(relevanceCondition):
    def wrapper(edgesList, superGraph, superGraphEdges):
        return relevanceCondition.isRelevant(edgesList, superGraph, superGraphEdges)
    return [wrapper]


def hasNBorders(n):
    def wrapper(edgesList, superGraph, superGraphEdges):
        externalVertex = superGraph.externalVertex
        borders = set()
        for e in edgesList:
            v1, v2 = e.nodes
            if v1 == externalVertex:
                borders.add(v2)
            if v2 == externalVertex:
                borders.add(v1)
        return len(borders) == n
    return [wrapper]


oneIrreducible = graphFilter(graph_operations.isGraph1Irreducible)
connected = graphFilter(graph_operations.isGraphConnected)
noTadpoles = graphFilter(graph_operations.hasNoTadpolesInCounterTerm)
vertexIrreducible = graphFilter(graph_operations.isGraphVertexIrreducible)
