#!/usr/bin/python
# -*- coding:utf8
import graph_state

import graphine
from graphine import filters

import sys


class Model(object):
    relevantGraphsLegsCard = set([2, 4])
    edgeIRWeight = -2
    spaceDim = 4

    # noinspection PyUnusedLocal
    def isUVRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        return len(subgraph.edges(subgraph.externalVertex)) in self.relevantGraphsLegsCard

    def isIRRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        borderNodes = reduce(lambda x, y: x | y,
                             map(lambda x: set(x.nodes), subgraph.edges(subgraph.externalVertex))) - set([-1])
        if len(borderNodes) != 2:
            return False
        nEdges = len(edgesList) - len(subgraph.edges(subgraph.externalVertex))
        nVertexes = len(subgraph.vertexes()) - 1
        nLoop = nEdges - nVertexes + 1
        subgraphIRIndex = nEdges * self.edgeIRWeight + (nLoop + 1) * self.spaceDim
        return subgraphIRIndex <= 0


phi4 = Model()
subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isUVRelevant(phi4))

subgraphIRFilters = (filters.connected
                     + filters.isIRRelevant(phi4))

g = graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1]))

subgraphsUV = [str(subg.toGraphState()) for subg in
               g.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asMinimalGraph)]

print subgraphsUV

subgraphsIR = [str(subg.toGraphState()) for subg in
               g.xRelevantSubGraphs(subgraphIRFilters, graphine.Representator.asMinimalGraph)]

print subgraphsIR