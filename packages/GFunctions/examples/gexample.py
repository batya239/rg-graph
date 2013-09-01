#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys

import gfunctions
import graphine
import graph_state


gfunctions.graph_storage.initStorage(withFunctions=True)
gfunctions.rprime_storage.initStorage()

gs = graph_state.GraphState.fromStr("e12-233-34-4-e-")
graph = graphine.Graph.initEdgesColors(graphine.Graph(gs))

reducer = gfunctions.GGraphReducer(graph)

while reducer.nextIteration():
    pass

print reducer.iterationGraphs
print reducer.iterationValues

gfunctions.rprime_storage.closeStorage(revert=False, doCommit=True, commitMessage="example")
gfunctions.graph_calculator.dispose()


