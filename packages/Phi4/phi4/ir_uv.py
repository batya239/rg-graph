#!/usr/bin/python
# -*- coding: utf8
import rggraphutil

__author__ = 'daddy-bear'

import graph_state

import graphine
import graphine.filters as filters
import sys
import const
import inject

#todo assumed that weight of any line is 1


def uvIndexTadpole(graph):
    nEdges = len(graph.allEdges()) - len(graph.edges(graph.external_vertex))
    assert_right_edges(graph.allEdges())
    index = nEdges * const.EDGE_WEIGHT + numeratorsCount(graph.allEdges()) + (graph.getLoopsCount() + 1) * inject.instance("space_dimension_int")
    return index


def uvIndex(graph):
    nEdges = len(graph.allEdges()) - len(graph.edges(graph.external_vertex))
    assert_right_edges(graph.allEdges())
    index = nEdges * const.EDGE_WEIGHT + numeratorsCount(graph.allEdges()) + graph.getLoopsCount() * inject.instance("space_dimension_int")
    return index


def numeratorsCount(edgesList):
    _numeratorsCount = 0
    for e in edgesList:
        if e.fields is None:
            break
        else:
            if e.arrow is not None and not e.arrow.is_null():
                _numeratorsCount += 1
    return _numeratorsCount


class UVRelevanceCondition(object):
    def __init__(self, space_dim):
        self._space_dim = space_dim

    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subGraph = graphine.Representator.asGraph(edgesList, superGraph.external_vertex)
        nEdges = len(edgesList) - len(subGraph.edges(subGraph.external_vertex))
        nVertexes = len(subGraph.vertices()) - 1
        nLoop = nEdges - nVertexes + 1
        assert_right_edges(edgesList)
        subGraphUVIndex = nEdges * const.EDGE_WEIGHT + numeratorsCount(edgesList) + nLoop * self._space_dim
        return subGraphUVIndex >= 0


class IRRelevanceCondition(object):
    def __init__(self, space_dim):
        self._space_dim = space_dim

    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subGraph = graphine.Representator.asGraph(edgesList, superGraph.external_vertex)

        borderNodes = subGraph.getBoundVertexes()

        if len(borderNodes) > 2:
            return False
        nEdges = subGraph.getAllInternalEdgesCount()
        nLoop = subGraph.getLoopsCount()
        assert_right_edges(edgesList)
        subGraphIRIndex = nEdges * const.EDGE_WEIGHT + numeratorsCount(edgesList) + (nLoop + 1) * self._space_dim
        # invalid result for e12-e333-3-- (there is no IR subGraphs)
        if subGraphIRIndex > 0:
            return False

        superBorderNodes = reduce(lambda x, y: x | y,
                                  map(lambda x: set(x.nodes), superGraph.edges(superGraph.external_vertex))) - \
                                  set([superGraph.external_vertex])

        connectionEquivalence = _MergeResolver(superGraph.external_vertex, borderNodes, superBorderNodes)
        for e in superGraphEdges:
            connectionEquivalence.addEdge(e)
        return connectionEquivalence.isRelevant()


class _MergeResolver(object):
    def __init__(self, externalVertex, cutVertexes, superBorderNodes):
        self._disjointSet = graphine.graph_operations._DisjointSet()
        self._borders = rggraphutil.emptyListDict()
        self._connectedComponents = list()
        self._cutVertexes = set(cutVertexes)
        self._externalVertex = externalVertex
        self._hasBorderJumpers = False
        self._superBorderVertexes = superBorderNodes

    def addEdge(self, e):
        if self._hasBorderJumpers:
            return
        vs = filter(lambda v: v not in self._cutVertexes and v is not self._externalVertex, e.nodes)
        length = len(vs)
        if length == 0:
            if not self._hasBorderJumpers and len(filter(lambda v: v is not self._externalVertex, e.nodes)) == 2:
                self._hasBorderJumpers = True
        elif length == 1:
            self._disjointSet.addKey(vs[0])
            border = filter(lambda v: v is not vs[0], e.nodes)[0]
            if border is not self._externalVertex:
                self._borders[vs[0]].append(border)
        else:
            #lenght = 2
            self._disjointSet.union((vs[0], vs[1]))

    def isRelevant(self):
        if self._hasBorderJumpers:
            return True
        components = self._disjointSet.getConnectedComponents()
        if len(components) == 1:
            return True
        countWith2Tails = 0
        for component in components:
            borders = list()
            superBorderNodesCount = 0
            for v in component:
                if v in self._superBorderVertexes:
                    superBorderNodesCount += 1
                borders += self._borders[v]
            if len(set(borders)) == 2 or (len(borders) == 1 and superBorderNodesCount > 0):
                countWith2Tails += 1

        return countWith2Tails > 1


def assert_right_edges(edges):
    for e in edges:
        if e.is_external():
            continue
        if e.weight:
            assert e.weight.b == 0, e
            assert e.weight.a == 1, e