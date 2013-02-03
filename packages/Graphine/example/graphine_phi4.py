#!/usr/bin/python
# -*- coding:utf8
import graph_state

import graphine
from graphine import filters

import sys


class Model:
    relevantGraphsLegsCard = set([2, 4])

    def isRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        return len(subgraph.edges(subgraph.externalVertex)) in self.relevantGraphsLegsCard


phi4 = Model()
subgraphFilters = (  filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.isRelevant(phi4))
g = graphine.Graph(graph_state.GraphState.fromStr(sys.argv[1]))

current = [str(subg.toGraphState()) for subg in
           g.xRelevantSubGraphs(subgraphFilters, graphine.Representator.asMinimalGraph)]

print current
