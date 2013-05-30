#!/usr/bin/python
# -*- coding: utf8
import unittest

from graph_state import graph_state as gs
import graph as gr
import graph_operations
import filters

simpleEdges = tuple([gs.Edge((0, 1)), gs.Edge((1, 2)), gs.Edge((0, 2)), gs.Edge((-1, 0)), gs.Edge((-1, 2))])
simpleGraphState = gs.GraphState(simpleEdges)
simpleGraph = gr.Graph(simpleGraphState)

edges = tuple([gs.Edge(p) for p in [(-1, 0), (0, 1), (0, 2), (1, 2), (2, 3), (1, 3), (3, -1)]])
graphState = gs.GraphState(edges)
graph = gr.Graph(graphState)

subEdges = tuple([gs.Edge(p) for p in [(0, 1), (0, 2), (1, 2)]])
subGraphState = gs.GraphState(subEdges)
subGraph = gr.Graph(subGraphState)


@filters.graphFilter
def twoEdgesFilter(edgesList, superGraph, superGraphEdges):
    externalVertex = superGraph.externalVertex
    notExternalEdges = list()
    for e in edgesList:
        if externalVertex not in set(e.nodes):
            notExternalEdges.append(e)
    return len(notExternalEdges) == 2


class GraphTestCase(unittest.TestCase):
    def testIndexableEdges(self):
        graph = gr.Graph(gs.GraphState.fromStr("e11-e-::"))
        indexableEdges = graph.allEdges(withIndex=True)
        indexes = set()
        for ie in indexableEdges:
            indexes.add(ie.index)
        self.assertSetEqual(indexes, set([0, 1, 2, 3]))

        i = 100
        for ie in indexableEdges:
            ie.myBestEdgeProperty = i
            i += 1

        myBestProperties = set()
        for ie in indexableEdges:
            myBestProperties.add(ie.myBestEdgeProperty)

        self.assertSetEqual(myBestProperties, set([100, 101, 102, 103]))

    def testCreationAndConvertingToGraphState(self):
        self.assertEquals(simpleGraph.toGraphState(), simpleGraphState)
        self.assertSetEqual(set(simpleGraph.allEdges()), set(simpleGraphState.edges))
        #
        self.assertEquals(graph.toGraphState(), graphState)
        self.assertSetEqual(set(graph.allEdges()), set(graphState.edges))

    def testGetRelevantSubGraphs(self):
        self.doTestGetRelevantSubGraphs("e111-e-::", 0)
        self.doTestGetRelevantSubGraphs("ee12-223-3-ee-::", 3)
        self.doTestGetRelevantSubGraphs("ee12-e3-445-455-5--::", 5)
        self.doTestGetRelevantSubGraphs("ee12-e22-e-::", 1)

        graph = gr.Graph(gs.GraphState.fromStr("e14-2-344-4-e-::"))
        current = [g for g in
                   graph.xRelevantSubGraphs(twoEdgesFilter, gr.Representator.asList)]
        print current[17]
        return graph_operations.isGraphConnected(current[1], graph, graph.allEdges())


    def testNextVertexIndex(self):
        self.assertEquals(simpleGraph.createVertexIndex(), 3)
        self.assertEquals(simpleGraph.createVertexIndex(), 4)

    def testGetVertexEdges(self):
        self.assertSetEqual(simpleGraph.vertexes(), set([-1, 0, 1, 2]))
        #
        self.assertSetEqual(graph.vertexes(), set([-1, 0, 1, 2, 3]))

    def testShrinkToPointInBatch(self):
        self.doTestShrinkToPointInBatch([(-1, 0), (0, 1), (0, 2), (1, 2), (2, 3), (1, 3), (3, -1)],
                                        [[(0, 1), (0, 2), (1, 2)], [(1, 3)]],
                                        'ee0-::')

        self.doTestShrinkToPointInBatch([(-1, 0), (0, 1), (0, 2), (1, 2), (1, 2), (2, 3), (1, 3), (3, -1)],
                                        [[(0, 1), (0, 2), (1, 2)], [(1, 3)]],
                                        'ee00-::')

        self.doTestShrinkToPointInBatch([(-1, 0), (0, 1), (0, 2), (1, 2), (1, 2), (0, 3), (1, 3), (2, -1)],
                                        [[(2, 1), (3, 2), (1, 3)], [(0, 1), (0, 2)]],
                                        'ee0-::')

    def testShrinkToPoint(self):
        self.doTestShrinkToPoint([(-1, 0), (0, 1), (0, 2), (1, 2), (2, 3), (1, 3), (3, -1)],
                                 [(0, 1), (0, 2), (1, 2)],
                                 'e11-e-::')

        self.doTestShrinkToPoint([(-1, 0), (0, 1), (0, 1), (0, 1), (1, -1)],
                                 [(0, 1), (0, 1)],
                                 'ee0-::')

    def doTestGetRelevantSubGraphs(self, nickelRepresentation, expected):
        graph = gr.Graph(gs.GraphState.fromStr(nickelRepresentation))
        testFilters = filters.noTadpoles + filters.oneIrreducible
        current = [g for g in
                   graph.xRelevantSubGraphs(testFilters, gr.Representator.asList)]
        if isinstance(expected, int):
            self.assertEquals(expected, len(current))
        elif isinstance(expected, list):
            self.assertSetEqual(set(current), set(expected))
            self.assertEquals(len(expected), len(current))

    def doTestShrinkToPointInBatch(self, edges, subGraphs, expectedGraphState):
        graphState = gs.GraphState([gs.Edge(e) for e in edges])
        graph = gr.Graph(graphState)
        newGraph = graph.batchShrinkToPoint(self.prepareGraphs(subGraphs))
        self.assertEquals(str(newGraph.toGraphState()), expectedGraphState)

    def doTestShrinkToPoint(self, edges, subEdges, expectedGraphState):
        graphState = gs.GraphState([gs.Edge(e) for e in edges])
        graph = gr.Graph(graphState)
        newGraph = graph.shrinkToPoint([gs.Edge(e) for e in subEdges])
        self.assertEquals(str(newGraph.toGraphState()), expectedGraphState)

    # noinspection PyMethodOverriding
    def assertSetEqual(self, set1, set2):
        assert set1 == set2, str(set1) + " != " + str(set2)

    def prepareEdges(self, edges):
        return [gs.Edge(e) for e in edges]

    def prepareGraphs(self, graphs):
        return [self.prepareEdges(g) for g in graphs]


if __name__ == "__main__":
    unittest.main()