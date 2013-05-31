#!/usr/bin/python
# -*- coding: utf8
import os

__author__ = 'daddy-bear'

import gfunctions
import gfunctions.graph_storage
import graph_state
import graphine


def calculateGraph(graph):
    x = 1
    for _g in gfunctions.xArbitrarilyPassMomentum(graph):
        reducer = gfunctions.GGraphReducer(_g)
        while reducer.nextIteration():
            pass
        print str(x) + ". " + str(_g) + " : " + str(reducer.getCurrentIterationValue())
        x += 1


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






