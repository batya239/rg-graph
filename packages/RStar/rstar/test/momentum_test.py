#!/usr/bin/python
# -*- coding: utf8
import unittest

import graph_util
import momentum


__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def testArbitrarilyPassMomentum(self):
        self.doTestArbitrarilyPassMomentum("ee12|23|3|ee|:(0,0)_(0,0)_(1,0)_(1,0)|(1,0)_(1,0)|(1,0)|(0,0)_(0,0)|:::", 3)
        self.doTestArbitrarilyPassMomentum("ee12|3|3|ee|:(0,0)_(0,0)_(1,0)_(1,0)|(1,0)|(1,0)|(0,0)_(0,0)|:::", 2)
        self.doTestArbitrarilyPassMomentum("11||:(1,0)_(1,0)||:::", 1)

    def testArbitraryPassMomentum(self):
        g = graph_util.graph_from_str("ee12|e23|44|e44||:(0,0)_(0,0)_(1,0)_(1,0)|(0,0)_(1,0)_(1,0)|(1,0)_(1,0)|(0,0)_(1,0)_(1,0)||:::")
        for x in momentum.arbitrarily_pass_momentum(g):
            self.assertFalse(str(x).startswith("ee"))

    def doTestArbitrarilyPassMomentum(self, graph_state_str, graphs_number):
        g = graph_util.graph_from_str(graph_state_str)
        graphs_with_passed_momentum = [x for x in momentum.arbitrarily_pass_momentum(g)]
        for _g in graphs_with_passed_momentum:
            self.assertEquals(len(_g.edges(_g.external_vertex)), 2)
        self.assertEquals(len(graphs_with_passed_momentum), graphs_number, graphs_with_passed_momentum)

if __name__ == "__main__":
    unittest.main()