#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import unittest
import reductor
import graphine
import sector
import swiginac
from rggraphenv import symbolic_functions


reductor.DEBUG = True

class ReductionTest(unittest.TestCase):
    def setUp(self):
        reductor.initialize(reductor.THREE_LOOP_REDUCTOR, reductor.TWO_LOOP_REDUCTOR)

    def test_tbubble(self):
        self.do_test("e12|23|3|e|:(0, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(1, 0)|(0, 0)|:",
                     "7.2123414189575657156-(4.6837737345148877438)*e+(24.069147509221049367)*e**2-(21.549990225248066582)*e**3")

    def test_tbubble_with_weight1(self):
        self.do_test("e12|23|3|e|:(0, 0)_(1, 0)_(1, 0)|(2, 0)_(1, 0)|(1, 0)|(0, 0)|:",
                     "-3.0-(3.0)*e**(-1)-(3.311654539582639764)*e**2-(7.6217394743351143255)*e**3+e**(-2)-(0.6370242568726971373)*e")

    def do_test(self, graph_as_string, expected_value_string):
        g = graphine.Graph.fromStr(graph_as_string)
        unsubstituted_actual = reductor.calculate(g)
        if not expected_value_string:
            self.assertIsNone(unsubstituted_actual)
            return
        expected = symbolic_functions.evaluate(expected_value_string)
        actual = unsubstituted_actual.evaluate(substitute_sectors=True,
                                               _d=symbolic_functions.D,
                                               series_n=4,
                                               remove_o=True)
        sub = (expected - actual).evalf().simplify_indexed()
        self.assertTrue(expected == actual.simplify_indexed() or swiginac.abs(
            (sub * symbolic_functions.e ** 5).subs(symbolic_functions.e == 1)).evalf().compare(10E-6) < 0,
                        "\nactual = " + str(actual.simplify_indexed().evalf()) +
                        "\nexpected = " + str(expected) + "\nsub = " + str(sub.evalf()))


if __name__ == "__main__":
    unittest.main()
