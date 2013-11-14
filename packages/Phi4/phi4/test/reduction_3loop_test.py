#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import unittest
import reductor
import graphine


class Reduction3LoopTest(unittest.TestCase):
    #def test_WAT1(self):
    #    storage.initStorage(theory.PHI4, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)
    #    reductor.initialize()
    #    print reductor.calculate(graphine.Graph.fromStr("e12-23-34-4-e-", initEdgesColor=True))
    #    storage.closeStorage(revert=True)

    def test_tbubble(self):
        reductor.initialize()
        print reductor.calculate(graphine.Graph.fromStr("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']"))

    #def do_test(self, graph_as_string, expected_value_string):
    #    g = graphine.Graph.fromStr(graph_as_string)
    #    reductor.initialize()
    #    print reductor.calculate(graphine.Graph.fromStr("e12-23-3-e-", initEdgesColor=True))


if __name__ == "__main__":
    unittest.main()
