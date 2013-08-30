#!/usr/bin/python
# -*- coding: utf8
import unittest

from graph_state import graph_state as gs
import graph as gr
import graph_operations as go


class ExternalVertexAware(object):
    def __init__(self, externalVertex):
        self.externalVertex = externalVertex


class GraphOperationsTestCase(unittest.TestCase):
    def testVertexIrreducibility(self):
        pass

    def testHasNoTadPoles(self):
        self.doTestHasNoTadPoles("ee18-233-334--ee5-667-78-88--::", [(1, 2), (1, 3), (2, 3), (2, 3)],
                                 expectedResult=False)
        self.doTestHasNoTadPoles("ee18-233-334--ee5-667-78-88--::", [(1, 2), (1, 3), (2, 3)],
                                 expectedResult=False)
        self.doTestHasNoTadPoles("ee18-233-334--ee5-667-78-88--::", [(1, 2), (1, 3), (1, 3), (2, 3), (2, 3)],
                                 expectedResult=True)
        self.doTestHasNoTadPoles("ee18-233-334--ee5-667-78-88--::", [(7, 8), (7, 8)],
                                 expectedResult=True)
        self.doTestHasNoTadPoles("e111-e-::", [(-1, 0), (-1, 0), (-1, 1), (-1, 1), (0, 1), (0, 1)],
                                 expectedResult=False)

    def test1Irreducibility(self):
        self.doTest1Irreducibility("ee12-e22-e-::", expectedResult=True)
        self.doTest1Irreducibility("ee0-::", expectedResult=True)
        self.doTest1Irreducibility("ee-::", expectedResult=True)
        self.doTest1Irreducibility("ee11-ee-::", expectedResult=True)
        self.doTest1Irreducibility("eee1-eee-::", expectedResult=False)
        self.doTest1Irreducibility("ee12-eee-eee-::", expectedResult=False)
        self.doTest1Irreducibility("ee12-ee2-ee-::", expectedResult=True)

    def testConnected(self):
        self.doTestConnected("ee0-::", expectedResult=True)
        self.doTestConnected("ee-::", expectedResult=True)
        self.doTestConnected("ee11-ee-::", expectedResult=True)
        self.doTestConnected("eee1-eee-::", expectedResult=True)
        self.doTestConnected("ee12-eee-eee-::", expectedResult=True)
        self.doTestConnected("ee12-ee1-ee-::", expectedResult=True)

    def testVertexIrreducibility(self):
        self.doTestVertexIrreducibility("ee11-22-ee-::", expectedResult=False)
        self.doTestVertexIrreducibility("ee12-ee2-ee-::", expectedResult=True)
        self.doTestVertexIrreducibility("011-22-2-::", expectedResult=False)
        self.doTestVertexIrreducibility("012-12-2-::", expectedResult=False)
        self.doTestVertexIrreducibility("012-222--::", expectedResult=False)
        self.doTestVertexIrreducibility("1122-22--::", expectedResult=True)
        self.doTestVertexIrreducibility("1-2-3-4--::", expectedResult=False)

    def doTestHasNoTadPoles(self, nickel, subGraphEdges, expectedResult):
        subGraphEdges = [gs.Edge(e) for e in subGraphEdges]
        graph = gr.Graph(gs.GraphState.fromStr(nickel))
        self.assertEquals(go.hasNoTadpolesInCounterTerm(subGraphEdges, graph, graph.allEdges()), expectedResult)

    def doTest1Irreducibility(self, nickel, expectedResult):
        graph = gr.Graph(gs.GraphState.fromStr(nickel))
        mockSuper = ExternalVertexAware(-1)
        self.assertEquals(go.isGraph1Irreducible(graph.allEdges(), mockSuper, []), expectedResult)

    def doTestConnected(self, nickel, expectedResult):
        graph = gr.Graph(gs.GraphState.fromStr(nickel))
        mockSuper = ExternalVertexAware(-1)
        self.assertEquals(go.isGraphConnected(graph.allEdges(), mockSuper, []), expectedResult)

    def doTestVertexIrreducibility(self, nickel, expectedResult):
        graph = gr.Graph(gs.GraphState.fromStr(nickel))
        mockSuper = ExternalVertexAware(-1)
        self.assertEquals(go.isGraphVertexIrreducible(graph.allEdges(), mockSuper, []), expectedResult)


if __name__ == "__main__":
    unittest.main()
