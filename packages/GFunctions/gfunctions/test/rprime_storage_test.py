#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import graphine
import rprime_storage
import symbolic_functions

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def setUp(self):
        rprime_storage.initStorage(False)

    def tearDown(self):
        rprime_storage.closeStorage(False, True, "commit from test")

    def DO_NOT_TEST_testSome(self):
        assert rprime_storage.getKR1(graphine.Graph(graph_state.GraphState.fromStr("e11-e-::")))
        graph = graphine.Graph(graph_state.GraphState.fromStr("ee11-e-::"))
        rprime_storage.putGraphKR1(graph, (
            symbolic_functions.polePart(symbolic_functions.evaluate("G(1,1)", (1, -1)))), "test", "test")
        assert rprime_storage.getKR1(graph)


if __name__ == "__main__":
    unittest.main()