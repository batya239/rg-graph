#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys

import gfunctions
import graphine
import graph_state


gfunctions.graph_storage.initStorage(withFunctions=True)
gfunctions.rprime_storage.initStorage()

gs = graph_state.GraphState.fromStr('e112-23-e4-e55-e55--')
graph = graphine.Graph.initEdgesColors(graphine.Graph(gs))

gfunctions.GGraphReducer.setDebug(True)
reducer = gfunctions.GGraphReducer(graph)

reducer.calculate()
print "result =", reducer.calculate()

gfunctions.rprime_storage.closeStorage(revert=False, doCommit=True, commitMessage="example")
gfunctions.graph_calculator.dispose()


