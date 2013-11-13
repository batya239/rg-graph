#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import graphine.filters as filters
import graphine
import ir_uv
import common

__author__ = 'daddy-bear'


uv = ir_uv.UV_RELEVANCE_CONDITION_4_DIM
ir = ir_uv.IR_RELEVANCE_CONDITION_4_DIM

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
        self.doTestIRCondition("e112-23-e4-45-55--", ['eee1-223-3-4-eee-::'])

    def testUVCondition3(self):
        g = graphine.Graph(graph_state.GraphState.fromStr("e1234-e255-3--5--:000000oiio-00000000-00--00--:"))
        uv = [str(x) for x in g.xRelevantSubGraphs(subgraphUVFilters, cutEdgesToExternal=True)]
        self.assertEqual(uv, ['eee11-e-:0000000000-00-:'])

    def doTestIRCondition(self, graphState, expectedGraphGraphs=list()):
        g = graphine.Graph(graph_state.GraphState.fromStr(graphState))
        self.assertEquals(set([str(subg.toGraphState()) for subg in
                               g.xRelevantSubGraphs(subgraphIRFilters, graphine.Representator.asMinimalGraph)]),
                               set(expectedGraphGraphs))

if __name__ == "__main__":
    unittest.main()