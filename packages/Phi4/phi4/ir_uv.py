#!/usr/bin/python
# -*- coding: utf8
import rggraphutil

__author__ = 'daddy-bear'

import graph_state

import graphine
import graphine.filters as filters
import sys
import const


def uvIndex(graph):
    nEdges = len(graph.allEdges(withIndex=True)) - len(graph.edges(graph.externalVertex))
    nVertexes = len(graph.vertexes()) - 1
    nLoop = nEdges - nVertexes + 1
    index = nEdges * const.edgeUVWeight + nLoop * const.spaceDim
    return index


class UVRelevanceCondition(object):
    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        nEdges = len(edgesList) - len(subGraph.edges(subGraph.externalVertex))
        nVertexes = len(subGraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subGraphUVIndex = nEdges * const.edgeUVWeight + nLoop * const.spaceDim
        return subGraphUVIndex >= 0


class IRRelevanceCondition(object):
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)

        externalEdges = subGraph.edges(subGraph.externalVertex)
        borderNodes = reduce(lambda x, y: x | y,
                             map(lambda x: set(x.nodes), externalEdges)) - \
                             set([superGraph.externalVertex])

        if len(borderNodes) != 2:
            return False
        nEdges = len(edgesList) - len(externalEdges)
        nVertexes = len(subGraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subGraphIRIndex = nEdges * const.edgeIRWeight + (nLoop + 1) * const.spaceDim
        # invalid result for e12-e333-3-- (there is no IR subGraphs)
        if subGraphIRIndex > 0:
            return False

        superBorderNodes = reduce(lambda x, y: x | y,
                                  map(lambda x: set(x.nodes), superGraph.edges(superGraph.externalVertex))) - \
                                  set([superGraph.externalVertex])

        connectionEquivalence = _MergeResolver(superGraph.externalVertex, borderNodes, superBorderNodes)
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


def main():
    uv = UVRelevanceCondition()
    ir = IRRelevanceCondition()

    subGraphUVFilters = (filters.oneIrreducible
                         + filters.noTadpoles
                         + filters.vertexIrreducible
                         + filters.isRelevant(uv))

    subGraphIRFilters = (filters.connected + filters.isRelevant(ir))

    g = graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1]))

    print g.toGraphState()

    subGraphsUV = [str(subg.toGraphState()) for subg in
                   g.xRelevantSubGraphs(subGraphUVFilters, graphine.Representator.asMinimalGraph)]

    print "UV\n", subGraphsUV

    subGraphsIR = [str(subg.toGraphState()) for subg in
                   g.xRelevantSubGraphs(subGraphIRFilters, graphine.Representator.asMinimalGraph)]

    print "IR\n", subGraphsIR

if __name__ == "__main__":
    main()

