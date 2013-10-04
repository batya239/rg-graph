#!/usr/bin/python
# -*- coding: utf8
import graph_state
import graphine
import graphine.momentum as momentum
import rggraphutil
import gfunctions.common as common
import gfunctions.r as r
import gfunctions.symbolic_functions as symbolic_functions
import os

__author__ = 'daddy-bear'


def _calculate(g, useGraphCalculator=False):
    if len(g.edges(g.externalVertex)) == 2:
        withMomentumPassing = g,
    else:
        withMomentumPassing = [x for x in momentum.xPassExternalMomentum(g, common.defaultGraphHasNotIRDivergenceFilter)]
    result = None
    for graph in withMomentumPassing:
        if result is not None:
            break
        try:
            print graph
            result = r.KR1(graph, common.MSKOperation(),
                           common.defaultSubgraphUVFilter,
                           useGraphCalculator=useGraphCalculator)
        except common.CannotBeCalculatedError:
            pass
            print "can't calculate", graph
        except BaseException as e:
            print e, graph
            pass
    print ("OK " + str(g) + " = " + str(result)) if result else ("FAIL " + str(g))


def main():
    rggraphutil.env.storage.initStorage(rggraphutil.env.theory.PHI4,
                                        symbolic_functions.toInternalCode,
                                        graphStorageUseFunctions=True)

    loopsToFilter = int(6)
    tailsCount = int(4)
    assert 1 <= loopsToFilter <= 6
    assert tailsCount in (2, 4)

    graphsToCalculate = list()
    for l in open(os.path.join(os.getcwd(), "../../../phi4/graphs/e" + str(tailsCount) + "-6loop.lst")):
        graph = graphine.Graph(graph_state.GraphState.fromStr(l[:-1] + "::"))
        if graph.getLoopsCount() == loopsToFilter:
            graphsToCalculate.append(graphine.Graph.initEdgesColors(graph))

    for g in graphsToCalculate:
        _calculate(g)

    rggraphutil.env.storage.closeStorage(revert=False, doCommit=True, commitMessage=str(loopsToFilter) + "loops, 2tails, phi4_rprime.py")


if __name__ == "__main__":
    main()