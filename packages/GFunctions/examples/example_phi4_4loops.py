#!/usr/bin/python
# -*- coding: utf8
import os
import sys

__author__ = 'daddy-bear'

import gfunctions
import gfunctions.graph_storage
import gfunctions.rprime_storage
import graph_state
import graphine
import graphine.phi4


def calculateGraphRPrime(graph):
    calculated = False
    description = ""
    if len(graph.edges(graph.externalEdge)) == 4:
        description += "4tails_graph: " + graph.getPresentableStr()

    for _g in gfunctions.xPassExternalMomentum(graph, gfunctions.defaultGraphHasNotIRDivergenceFilter):
        try:
            gfunctions.doRPrime(_g, gfunctions.MSKOperation(), gfunctions.defaultSubgraphUVFilter, description)
            calculated = True
        except gfunctions.CannotBeCalculatedError as e:
            print e.message
    if calculated:
        print "OK", graph
    else:
        print "FAILED", graph


_SUBGRAPHS_IR_FILTER = (graphine.filters.connected + graphine.filters.isRelevant(graphine.phi4.IRRelevanceCondition()))


def hasIRSubGraphs(g):
    return len([x for x in g.xRelevantSubGraphs(_SUBGRAPHS_IR_FILTER, graphine.Representator.asMinimalGraph)]) != 0


def calculateRPrime(graphReducer):
    """
    NOT checking that graph hasn't IR subgraphs
    """
    assert graphReducer.isSuccesfulDone()


def main():
    gfunctions.graph_storage.initStorage(withFunctions=True)
    gfunctions.rprime_storage.initStorage()

    graphs4Loops = list()
    for l in open(os.path.join(os.getcwd(), "../../../phi4/graphs/e4-6loop.lst")):
        loopsCount = -1
        for c in l:
            if c == "-":
                loopsCount += 1
        if loopsCount == 4:
            graphs4Loops.append(
                graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(l[:-1] + "::"))))

    for g in graphs4Loops:
        calculateGraphRPrime(g)

    gfunctions.rprime_storage.closeStorage(revert=False, doCommit=True, commitMessage=sys.argv[3])


if __name__ == "__main__":
    main()






