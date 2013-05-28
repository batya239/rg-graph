#!/usr/bin/python
# -*- coding:utf8
import graph_state

import graphine
from graphine import filters

import sys


class UVRelevanceCondition(object):
    edgeUVWeight = -2
    spaceDim = 4

    # noinspection PyUnusedLocal
    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        nEdges = len(edgesList) - len(subgraph.edges(subgraph.externalVertex))
        nVertexes = len(subgraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subgraphUVIndex = nEdges * self.edgeUVWeight + (nLoop + 1) * self.spaceDim
        return subgraphUVIndex >= 0

class IRRelevanceCondition(object):
    edgeIRWeight = -2
    spaceDim = 4

    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        borderNodes = reduce(lambda x, y: x | y,
                             map(lambda x: set(x.nodes), subgraph.edges(subgraph.externalVertex))) - set([-1])
        if len(borderNodes) != 2:
            return False
        nEdges = len(edgesList) - len(subgraph.edges(subgraph.externalVertex))
        nVertexes = len(subgraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subgraphIRIndex = nEdges * self.edgeIRWeight + (nLoop + 1) * self.spaceDim
        # invalid result for e12-e333-3-- (there is no IR subgraphs)
        return subgraphIRIndex <= 0


uv = UVRelevanceCondition()
ir = IRRelevanceCondition()

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isRelevant(uv))

subgraphIRFilters = (filters.connected
                     + filters.isRelevant(ir))

g = graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1]))

subgraphsUV = [str(subg.toGraphState()) for subg in
               g.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asMinimalGraph)]

print subgraphsUV

subgraphsIR = [str(subg.toGraphState()) for subg in
               g.xRelevantSubGraphs(subgraphIRFilters, graphine.Representator.asMinimalGraph)]

print subgraphsIR
