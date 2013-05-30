#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
import graphine


def graphFilter(qualifier):
    """
    graphFilter should be used as decorator

    @graphFilter
    def myFilter(edgesList):
      ...
    """
    return [qualifier]


oneIrreducible = graphFilter(graphine.graph_operations.isGraph1Irreducible)
vertexIrreducible = graphFilter(graphine.graph_operations.isGraphVertexIrreducible)
connected = graphFilter(graphine.graph_operations.isGraphConnected)


class _StubExternalVertexAwareGraph(object):
    def __init__(self, externalVertex):
        self._externalVertex = externalVertex

    @property
    def externalVertex(self):
        return self._externalVertex


def _graphineWrapper(graphineFilter):
    def wrapper(graph):
        return graphineFilter(graph.allEdges(), _StubExternalVertexAwareGraph(graph.externalVertex), None)

    return [wrapper]


def xPassExternalMomentum(graph, filters=list()):
    for momentumPassing in xPickPassingExternalMomentum(graph, filters):
        yield passMomentOnGraph(graph, momentumPassing)


def xPickPassingExternalMomentum(graph, filters=list()):
    """
    find all cases for passing external momentum
    """
    externalEdges = graph.edges(graph.externalVertex)
    for edgesPair in itertools.combinations(externalEdges, 2):
        vertexes = set()
        for e in edgesPair:
            vertexes |= set(e.nodes)
        if len(vertexes) == 3:
            graphWithMomentumPassing = graph.deleteEdges(copy.copy(edgesPair))
            isValid = True
            for f in filters:
                if not f(graphWithMomentumPassing):
                    isValid = False
                    break
            if isValid:
                yield edgesPair


def passMomentOnGraph(graph, momentumPassing):
    assert len(momentumPassing) == 2
    edgesToRemove = list()
    copiedMomentumPassing = list(momentumPassing)
    for e in graph.edges(graph.externalVertex):
        if e in copiedMomentumPassing:
            copiedMomentumPassing.remove(e)
        else:
            edgesToRemove.append(e)
    return graph.deleteEdges(edgesToRemove)