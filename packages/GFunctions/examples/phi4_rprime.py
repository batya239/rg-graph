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


def calculateGraphRPrime(graph):
    calculated = False
    description = ""
    if len(graph.externalEdges()) == 4:
        description += "4tails_graph: " + graph.getPresentableStr()

    for _g in gfunctions.xPassExternalMomentum(graph, gfunctions.defaultGraphHasNotIRDivergenceFilter):
        try:
            gfunctions.doRPrime(_g, gfunctions.MSKOperation(), gfunctions.defaultSubgraphUVFilter, description)
            calculated = True
        except gfunctions.CannotBeCalculatedError as e:
            print "\tcan't calculate:", e.message
    if calculated:
        print "OK", graph
    else:
        print "FAILED", graph


def main():
    gfunctions.graph_storage.initStorage(withFunctions=True)
    gfunctions.rprime_storage.initStorage()

    loopsToFilter = int(sys.argv[1])
    tailsCount = int(sys.argv[2])
    assert 1 <= loopsToFilter <= 6
    assert tailsCount in (2, 4)

    graphsToCalculate = list()
    for l in open(os.path.join(os.getcwd(), "../../../phi4/graphs/e" + str(tailsCount) + "-6loop.lst")):
        graph = graphine.Graph(graph_state.GraphState.fromStr(l[:-1] + "::"))
        if graph.calculateLoopsCount() == loopsToFilter:
            graphsToCalculate.append(graphine.Graph.initEdgesColors(graph))

    for g in graphsToCalculate:
        calculateGraphRPrime(g)
        
    gfunctions.rprime_storage.closeStorage(revert=False, doCommit=False, commitMessage=sys.argv[3])


if __name__ == "__main__":
    main()