#!/usr/bin/python
# -*- coding: utf8
import unittest

from graph_state import graph_state as gs
from graphine import graph as gr

simpleEdges = tuple([gs.Edge((0, 1)), gs.Edge((1, 2)), gs.Edge((0, 2)), gs.Edge((-1, 0)), gs.Edge((-1, 2))])
simpleGraphState = gs.GraphState(simpleEdges)
simpleGraph = gr.Graph(simpleGraphState)

edges = tuple([gs.Edge(p) for p in [(-1, 0), (0, 1), (0, 2), (1, 2), (2, 3), (1, 3), (3, -1)]])
graphState = gs.GraphState(edges)
graph = gr.Graph(graphState)

subEdges = tuple([gs.Edge(p) for p in [(0, 1), (0, 2), (1, 2)]])
subGraphState = gs.GraphState(subEdges)
subGraph = gr.Graph(subGraphState)


class GraphTestCase(unittest.TestCase):
    def testCreationAndConvertingToGraphState(self):
        self.assertEquals(simpleGraph.toGraphState(), simpleGraphState)
        self.assertSetEqual(set(simpleGraph.allEdges()), set(simpleGraphState.edges))
        #
        self.assertEquals(graph.toGraphState(), graphState)
        self.assertSetEqual(set(graph.allEdges()), set(graphState.edges))

    def testGetVertexEdges(self):
        self.assertSetEqual(simpleGraph.vertexes(), set([-1, 0, 1, 2]))
        #
        self.assertSetEqual(graph.vertexes(), set([-1, 0, 1, 2, 3]))

    def testShrinkToPoint(self):
        self.doTestShrinkToPoint([(-1, 0), (0, 1), (0, 2), (1, 2), (2, 3), (1, 3), (3, -1)],
                                 [(0, 1), (0, 2), (1, 2)],
                                 'e11-e-::')

        self.doTestShrinkToPoint([(-1, 0), (0, 1), (0, 1), (0, 1), (1, -1)],
                                 [(0, 1), (0, 1)],
                                 'ee0-::')

    def doTestShrinkToPoint(self, edges, subEdges, expectedGraphState):
        graphState = gs.GraphState([gs.Edge(e) for e in edges])
        graph = gr.Graph(graphState)
        newGraph = graph.shrinkToPoint([gs.Edge(e) for e in subEdges])
        self.assertEquals(str(newGraph.toGraphState()), expectedGraphState)
