#!/usr/bin/python
# -*- coding: utf8
import unittest
import graphine
import graph_state
import momentum

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def testArbitrarilyPassMomentum(self):
        self.doTestArbitrarilyPassMomentum("ee12-23-3-ee-::", 6)
        self.doTestArbitrarilyPassMomentum("ee12-3-3-ee-::", 6)

    def doTestArbitrarilyPassMomentum(self, graphStateStr, graphsNumber):
        g = graphine.Graph(graph_state.GraphState.fromStr(graphStateStr))
        graphsWithPassedMomentum = [x for x in momentum.xArbitrarilyPassMomentum(g)]
        for _g in graphsWithPassedMomentum:
            self.assertEquals(len(_g.edges(_g.externalVertex)), 2)
        self.assertEquals(len(graphsWithPassedMomentum), graphsNumber)




if __name__ == "__main__":
    unittest.main()