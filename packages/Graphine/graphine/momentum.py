#!/usr/bin/python
# -*- coding: utf8
import filters
import graph_operations

__author__ = 'daddy-bear'

import copy
import itertools
import graph_state

oneIrreducible = filters.graphFilter(graph_operations.isGraph1Irreducible)
vertexIrreducible = filters.graphFilter(graph_operations.isGraphVertexIrreducible)
connected = filters.graphFilter(graph_operations.isGraphConnected)


class _StubExternalVertexAwareGraph(object):
    def __init__(self, externalVertex):
        self._externalVertex = externalVertex

    @property
    def externalVertex(self):
        return self._externalVertex


def _graphine_wrapper(graphine_filter):
    def wrapper(graph):
        return graphine_filter(graph.allEdges(), _StubExternalVertexAwareGraph(graph.externalVertex), None)

    return [wrapper]


def xPassExternalMomentum(graph, filters=list()):
    for momentumPassing in xPickPassingExternalMomentum(graph, filters):
        yield passMomentOnGraph(graph, momentumPassing)


def xPickPassingExternalMomentum(graph, filters=list()):
    """
    chooses 2-combinations of external nodes
    """
    external_edges = graph.edges(graph.externalVertex)
    for edgesPair in itertools.combinations(_choose_external_edges_with_different_vertices(external_edges), 2):
        vertices = set()
        for e in edgesPair:
            vertices |= set(e.nodes)
        if len(vertices) == 3:
            graph_with_momentum_passing = graph.deleteEdges(external_edges).addEdges(list(edgesPair))
            is_valid = True
            for f in filters:
                if not f(graph_with_momentum_passing):
                    is_valid = False
                    break
            if is_valid:
                yield max(edgesPair), min(edgesPair)


def _choose_external_edges_with_different_vertices(edges):
    used_vertices = set()
    result = []
    for e in edges:
        v = e.internal_nodes[0]
        if v not in used_vertices:
            used_vertices.add(v)
            result.append(e)
    return result


def passMomentOnGraph(graph, momentum_passing):
    assert len(momentum_passing) == 2
    edges_to_remove = list()
    copied_momentum_passing = list(momentum_passing)
    for e in graph.edges(graph.externalVertex):
        if e in copied_momentum_passing:
            copied_momentum_passing.remove(e)
        else:
            edges_to_remove.append(e)
    return graph.deleteEdges(edges_to_remove)


def arbitrarilyPassMomentumWithPreferable(graph, prefer_condition):
    preferred = list()
    not_preferred = list()
    for g in set([g for g in xArbitrarilyPassMomentum(graph)]):
        if prefer_condition(g):
            preferred.append(g)
        else:
            not_preferred.append(g)
    return preferred, not_preferred


def xArbitrarilyPassMomentum(graph):
    """
    find ALL (NO CONDITIONS) cases for momentum passing.
    """

    #ex-ex
    passing = set([x for x in xPickPassingExternalMomentum(graph)])
    for momentumPassing in passing:
        yield passMomentOnGraph(graph, momentumPassing)

    #ex-in
    external_vertex = graph.externalVertex
    external_edges = graph.edges(external_vertex)
    internal_vertices = graph.vertices() - set(reduce(lambda x, y: x | y, map(lambda x: set(x.nodes), external_edges), set())
                                              - set([external_vertex])) - set([external_vertex])

    visited_vertices = set()
    for e in external_edges:
        v = filter(lambda _v: _v != external_vertex, e.nodes)

        if v in visited_vertices:
            continue
        visited_vertices.add(v)

        edges_to_remove = copy.copy(external_edges)
        edges_to_remove.remove(e)
        _g = graph.deleteEdges(edges_to_remove)
        for v in internal_vertices:
            yield _g.addEdge(graph_state.Edge((v, external_vertex), external_node=external_vertex, colors=(0, 0)))

    #in-in
    _g = graph.deleteEdges(external_edges)
    for vs in itertools.combinations(internal_vertices, 2):
        yield _g.addEdges([graph_state.Edge((vs[0], external_vertex), external_node=external_vertex, colors=(0, 0)),
                          graph_state.Edge((vs[1], external_vertex), external_node=external_vertex, colors=(0, 0))])