#!/usr/bin/python
# -*- coding: utf8
import os

__author__ = 'daddy-bear'

import gfunctions
import gfunctions.graph_storage
import graph_state
import graphine
import graphine.phi4


def calculateGraph(graph):
    x = 1
    calculated = False
    calculatedWithRPrime = False
    for _g in gfunctions.xArbitrarilyPassMomentum(graph):
        reducer = gfunctions.GGraphReducer(_g)
        while reducer.nextIteration():
            pass
        if reducer.isSuccesfulDone():
            calculated = True
            value = reducer.getFinalValue()
            _hasIRSubgraphs = hasIRSubGraphs(_g)
            if not _hasIRSubgraphs:
                calculatedWithRPrime = True
            print str(x) + ". " + str(_g) + " : " + str(value) + " : IR = " + str(_hasIRSubgraphs)
            if not _hasIRSubgraphs:
                pass
        else:
            print str(x) + ". " + str(_g) + " : NO RESULT", reducer.getCurrentIterationGraph()
        x += 1
    if calculated:
        print "\n\nOK(" + ("R'" if calculatedWithRPrime else "R*") + ")", graph, '\n\n'
    else:
        print "\n\nFAILED", graph, '\n\n'


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
        calculateGraph(g)


if __name__ == "__main__":
    main()






