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
    nEdges = len(graph.allEdges()) - len(graph.edges(graph.externalVertex))
    nVertexes = len(graph.vertices()) - 1
    nLoop = nEdges - nVertexes + 1
    index = nEdges * const.EDGE_WEIGHT + nLoop * const.SPACE_DIM_PHI4
    return index


def numeratorsCount(edgesList):
    _numeratorsCount = 0
    for e in edgesList:
        if e.fields is None:
            break
        else:
            if e.fields != const.EMPTY_NUMERATOR:
                _numeratorsCount += 1
    return _numeratorsCount


class UVRelevanceCondition(object):
    def __init__(self, space_dim):
        self._space_dim = space_dim

    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        nEdges = len(edgesList) - len(subGraph.edges(subGraph.externalVertex))
        nVertexes = len(subGraph.vertices()) - 1
        nLoop = nEdges - nVertexes + 1
        subGraphUVIndex = nEdges * const.EDGE_WEIGHT + numeratorsCount(edgesList) + nLoop * self._space_dim
        return subGraphUVIndex >= 0


UV_RELEVANCE_CONDITION_4_DIM = UVRelevanceCondition(const.SPACE_DIM_PHI4)
UV_RELEVANCE_CONDITION_6_DIM = UVRelevanceCondition(const.SPACE_DIM_PHI3)


class IRRelevanceCondition(object):
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)

        externalEdges = subGraph.edges(subGraph.externalVertex)
        borderNodes = reduce(lambda x, y: x | y,
                             map(lambda x: set(x.nodes), externalEdges)) - \
                             set([superGraph.externalVertex])

        if len(borderNodes) > 2:
            return False
        nEdges = len(edgesList) - len(externalEdges)
        nVertexes = len(subGraph.vertices()) - 1
        nLoop = nEdges - nVertexes + 1
        subGraphIRIndex = nEdges * const.EDGE_WEIGHT + numeratorsCount(edgesList) + (nLoop + 1) * const.                                                                           SPACE_DIM_PHI4
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


IR_RELEVANCE_CONDITION_4_DIM = IRRelevanceCondition()


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
    uv = UV_RELEVANCE_CONDITION_4_DIM
    ir = IR_RELEVANCE_CONDITION_4_DIM

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

