#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys

import gfunctions
import graphine
import graph_state


gs = graph_state.GraphState.fromStr(sys.argv[1])
graph = graphine.Graph.initEdgesColors(graphine.Graph(gs))

reducer = gfunctions.GGraphReducer(graph)

while reducer.nextIteration():
    pass

print reducer.iterationGraphs
print reducer.iterationValues


