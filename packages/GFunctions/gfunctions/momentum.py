#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
import graphine
import graph_state


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
    chooses 2-combinations of external nodes
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


def xArbitrarilyPassMomentum(graph):
    """
    find ALL (NO CONDITIONS) cases for momentum passing.
    """

    #ex-ex
    passing = set([x for x in xPickPassingExternalMomentum(graph)])
    for momentumPassing in passing:
        yield passMomentOnGraph(graph, momentumPassing)

    #ex-in
    externalVertex = graph.externalVertex
    externalEdges = graph.edges(externalVertex)

    internalVertexes = graph.vertexes() - set(reduce(lambda x, y: x | y, map(lambda x: set(x.nodes), externalEdges)) - set([externalVertex])) - set([externalVertex])

    visitedVertexes = set()
    for e in externalEdges:
        v = filter(lambda v: v != externalVertex, e.nodes)

        if v in visitedVertexes:
            continue
        visitedVertexes.add(v)

        edgesToRemove = copy.copy(externalEdges)
        edgesToRemove.remove(e)
        _g = graph.deleteEdges(edgesToRemove)
        for v in internalVertexes:
            yield _g.addEdge(graph_state.Edge((v, externalVertex), external_node=externalVertex, colors=(0, 0)))

    #in-in
    _g = graph.deleteEdges(externalEdges)
    for vs in itertools.combinations(internalVertexes, 2):
        yield _g.addEdges([graph_state.Edge((vs[0], externalVertex), external_node=externalVertex, colors=(0, 0)),
                          graph_state.Edge((vs[1], externalVertex), external_node=externalVertex, colors=(0, 0))])
