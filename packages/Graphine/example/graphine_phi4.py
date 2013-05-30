#!/usr/bin/python
# -*- coding:utf8
import graph_state

import graphine
from graphine import filters
import graphine.graph_operations

import sys


class UVRelevanceCondition(object):
    """
    supported only 2-tails graphs
    """
    edgeUVWeight = -2
    spaceDim = 4

    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        nEdges = len(edgesList) - len(subgraph.edges(subgraph.externalVertex))
        nVertexes = len(subgraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subgraphUVIndex = nEdges * self.edgeUVWeight + nLoop * self.spaceDim
        if subgraphUVIndex >= 0:
            print subgraphUVIndex, nEdges, nLoop
        return subgraphUVIndex >= 0


class IRRelevanceCondition(object):
    edgeIRWeight = -2
    spaceDim = 4

    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)

        borderNodes = reduce(lambda x, y: x | y,
                             map(lambda x: set(x.nodes), subgraph.edges(subgraph.externalVertex))) - \
                      set([subgraph.externalVertex])

        notBorderVertexes = reduce(lambda x, y: x | y,
                                   map(lambda x: set(x.nodes), subgraph.allEdges())) \
                            - set(borderNodes) - set([subgraph.externalVertex])

        for v in notBorderVertexes:
            if not len(subgraph.edges(v)) == len(superGraph.edges(v)):
                return False

        if len(borderNodes) != 2:
            return False
        nEdges = len(edgesList) - len(subgraph.edges(subgraph.externalVertex))
        nVertexes = len(subgraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subgraphIRIndex = nEdges * self.edgeIRWeight + (nLoop + 1) * self.spaceDim
        # invalid result for e12-e333-3-- (there is no IR subgraphs)
        if subgraphIRIndex > 0:
            return False

        connectionEquivalence = _MergeResolver(superGraph.externalVertex, borderNodes)
        for e in superGraphEdges:
            connectionEquivalence.addEdge(e)
        return connectionEquivalence.isRelevant()


class _MergeResolver(object):
    def __init__(self, externalVertex, cutVertexes):
        self._disjointSet = graphine.graph_operations._DisjointSet()
        self._borders = dict()
        self._connectedComponents = list()
        self._cutVertexes = set(cutVertexes)
        self._externalVertex = externalVertex

    def addEdge(self, e):
        vs = filter(lambda v: v not in self._cutVertexes and v is not self._externalVertex, e.nodes)
        length = len(vs)
        if length == 0:
            return
        elif length == 1:
            self._disjointSet.addKey(vs[0])
            border = filter(lambda v: v is not vs[0], e.nodes)[0]
            if vs[0] in self._borders:
                self._borders[vs[0]].append(border)
            else:
                self._borders[vs[0]] = [border]
        else:
            #lenght = 2
            self._disjointSet.union((vs[0], vs[1]))

    def isRelevant(self):
        components = self._disjointSet.getConnectedComponents()
        if len(components) == 1:
            return True
        countWith2Tails = 0
        for component in components:
            borders = list()
            for v in component:
                borders += self._borders[v]
            if len(borders) == 2:
                countWith2Tails += 1

        return countWith2Tails > 1


uv = UVRelevanceCondition()
ir = IRRelevanceCondition()

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isRelevant(uv))

subgraphIRFilters = (filters.connected + filters.isRelevant(ir))

g = graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1]))

print g.toGraphState()

subgraphsUV = [str(subg.toGraphState()) for subg in
               g.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asMinimalGraph)]

print "UV\n", subgraphsUV

subgraphsIR = [str(subg.toGraphState()) for subg in
               g.xRelevantSubGraphs(subgraphIRFilters, graphine.Representator.asMinimalGraph)]

print "IR\n", subgraphsIR
