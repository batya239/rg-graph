#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import unittest
import reductor
import graphine
from rggraphenv import symbolic_functions


class ReductionTest(unittest.TestCase):
    #def test_WAT1(self):
    #    storage.initStorage(theory.PHI4, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)
    #    reductor.initialize()
    #    print reductor.calculate(graphine.Graph.fromStr("e12-23-34-4-e-", initEdgesColor=True))
    #    storage.closeStorage(revert=True)

    def setUp(self):
        reductor.initialize(reductor.THREE_LOOP_REDUCTOR, reductor.TWO_LOOP_REDUCTOR)

    #def test_tbubble(self):
    #    print reductor.calculate(graphine.Graph.fromStr("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']"))
    #
    #def test_E12_23_34_4_E_(self):
    #    print symbolic_functions.series(reductor.calculate(graphine.Graph.fromStr("e12-23-34-4-e-", initEdgesColor=True)), symbolic_functions.e, 0, 5, remove_order=True).evalf()

    #def test_E12_34_35_4_5_E_(self):
    #    calculated = reductor.calculate(graphine.Graph.fromStr("e12-34-35-4-5-e-", initEdgesColor=True))
    #    print symbolic_functions.series(calculated, symbolic_functions.e, 0, 5, remove_order=True).evalf()

    def test_E12_23_34_4_E_(self):
        calculated = reductor.calculate(graphine.Graph.fromStr("e12-23-34-4-e-", initEdgesColor=True))
        print symbolic_functions.series(calculated, symbolic_functions.e, 0, 5, remove_order=True).evalf()

    #def do_test(self, graph_as_string, expected_value_string):
    #    g = graphine.Graph.fromStr(graph_as_string)
    #    reductor.initialize()
    #    print reductor.calculate(graphine.Graph.fromStr("e12-23-3-e-", initEdgesColor=True))


if __name__ == "__main__":
    unittest.main()
