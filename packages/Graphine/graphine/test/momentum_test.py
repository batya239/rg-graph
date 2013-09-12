#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph
import graph_state
import momentum

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def testArbitrarilyPassMomentum(self):
        self.doTestArbitrarilyPassMomentum("ee12-23-3-ee-::", 6)
        self.doTestArbitrarilyPassMomentum("ee12-3-3-ee-::", 6)
        self.doTestArbitrarilyPassMomentum("11--", 1)

    def testArbitraryPassMomentum(self):
        g = graph.Graph.initEdgesColors(graph.Graph(graph_state.GraphState.fromStr("ee12-e23-44-e44--::")))
        for x in momentum.xArbitrarilyPassMomentum(g):
            self.assertFalse(str(x).startswith("ee"))

    def doTestArbitrarilyPassMomentum(self, graphStateStr, graphsNumber):
        g = graph.Graph.initEdgesColors(graph.Graph(graph_state.GraphState.fromStr(graphStateStr)))
        graphsWithPassedMomentum = [x for x in momentum.xArbitrarilyPassMomentum(g)]
        for _g in graphsWithPassedMomentum:
            self.assertEquals(len(_g.edges(_g.externalVertex)), 2)
        self.assertEquals(len(graphsWithPassedMomentum), graphsNumber, graphsWithPassedMomentum)

if __name__ == "__main__":
    unittest.main()