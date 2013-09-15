#!/usr/bin/python
# -*- coding: utf8
import os
import sys
import rggraphutil.env.theory

__author__ = 'daddy-bear'

import gfunctions
import rggraphutil.env.storage
import graph_state
import graphine


def calculateGraphRPrime(graph):
    calculated = False
    description = ""
    if len(graph.externalEdges()) == 4:
        description += "4tails_graph: " + graph.getPresentableStr()

    for _g in gfunctions.xPassExternalMomentum(graph, gfunctions.defaultGraphHasNotIRDivergenceFilter):
        try:
            gfunctions.r.KR1(_g, gfunctions.MSKOperation(), gfunctions.defaultSubgraphUVFilter, description=description)
            calculated = True
        except gfunctions.CannotBeCalculatedError as e:
            print "\tcan't calculate:", e.message
    if calculated:
        print "OK", graph
    else:
        print "FAILED", graph


def main():
    rggraphutil.env.storage.initStorage(rggraphutil.env.theory.PHI4,
                                        gfunctions.symbolic_functions.toInternalCode,
                                        graphStorageUseFunctions=True)

    loopsToFilter = int(6)
    tailsCount = int(2)
    assert 1 <= loopsToFilter <= 6
    assert tailsCount in (2, 4)

    graphsToCalculate = list()
    for l in open(os.path.join(os.getcwd(), "../../../phi4/graphs/e" + str(tailsCount) + "-6loop.lst")):
        graph = graphine.Graph(graph_state.GraphState.fromStr(l[:-1] + "::"))
        if graph.getLoopsCount() == loopsToFilter:
            graphsToCalculate.append(graphine.Graph.initEdgesColors(graph))

    for g in graphsToCalculate:
        calculateGraphRPrime(g)
        
    rggraphutil.env.storage.closeStorage(revert=False, doCommit=False, commitMessage="phi4_rprime.py")


if __name__ == "__main__":
    main()