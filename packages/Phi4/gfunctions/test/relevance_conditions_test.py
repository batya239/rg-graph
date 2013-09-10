#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import filters
import graphine
import relevance_conditions

__author__ = 'daddy-bear'


uv = relevance_conditions.UVRelevanceCondition()
ir = relevance_conditions.IRRelevanceCondition()

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isRelevant(uv))

subgraphIRFilters = (filters.connected + filters.isRelevant(ir))


class Phi4Test(unittest.TestCase):
    def testIRCondition(self):
        self.doTestIRCondition("e12-34-34--e-", ["ee1-2-ee-::"])
        self.doTestIRCondition("e112-e2--", ["eee1-2-eee-::"])
        self.doTestIRCondition("e123-224-4-4-e-", ["eee1-2-eee-::"])

    def doTestIRCondition(self, graphState, expectedGraphGraphs=list()):
        g = graphine.Graph(graph_state.GraphState.fromStr(graphState))
        self.assertEquals(set([str(subg.toGraphState()) for subg in
                               g.xRelevantSubGraphs(subgraphIRFilters, graphine.Representator.asMinimalGraph)]),
                               set(expectedGraphGraphs))

if __name__ == "__main__":
    unittest.main()