#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import filters
import graph
import phi4

__author__ = 'daddy-bear'


uv = phi4.UVRelevanceCondition()
ir = phi4.IRRelevanceCondition()

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isRelevant(uv))

subgraphIRFilters = (filters.connected + filters.isRelevant(ir))


class Phi4Test(unittest.TestCase):
    def testIRCondition(self):
        self.doTestIRCondition("e12-34-34--e-::", ["ee1-2-ee-::"])
        self.doTestIRCondition("e112-e2--::", ["eee1-2-eee-::"])

    def doTestIRCondition(self, graphState, expectedGraphGraphs=list()):
        g = graph.Graph(graph_state.GraphState.fromStr(graphState))
        self.assertEquals(set([str(subg.toGraphState()) for subg in
                               g.xRelevantSubGraphs(subgraphIRFilters, graph.Representator.asMinimalGraph)]),
                               set(expectedGraphGraphs))

if __name__ == "__main__":
    unittest.main()