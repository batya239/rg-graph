#!/usr/bin/python
# -*- coding: utf8
import graph_state
import graphine

__author__ = 'dima'

class XSpaceRepresentation(object):
    def __init__(self, diagram):
        if isinstance(diagram, str):
            self._graph = graphine.Graph(graph_state.GraphState.fromStr(diagram))
        elif isinstance(diagram, graph_state.GraphState):
            self._graph = graphine.Graph(diagram)
        elif isinstance(diagram, graphine.Graph):
            self._graph = diagram

        self._graph = graphine.Graph.initEdgesColors(self._graph)
        assert self._graph.edges(self._graph.externalVertex) == 2, "diagram should has correct momentum flow"

    @staticmethod
    def _doXSpaceRepresentation(self):
        propagators = set()
        for e in self._graph.allEdges():
            propagators.add(XSpaceRepresentation._buildPropagator(e))


    @staticmethod
    def _buildPropagator(edge):
        pass

