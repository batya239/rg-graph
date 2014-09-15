#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import unittest
import reductor
import graphine
import sector
import swiginac
import two_and_three_loops
import four_loops
import graph_state
import graph_util
from rggraphenv import symbolic_functions


reductor.DEBUG = True


class ReductionTest(unittest.TestCase):
    def setUp(self):
        reductor.initialize(two_and_three_loops.THREE_LOOP_REDUCTOR, two_and_three_loops.TWO_LOOP_REDUCTOR)

    def test_tbubble(self):
        self.do_test("e12|23|3|e|:0_1|1_1|1|1|0|",
                     "7.2123414189575657156-(4.6837737345148877438)*e+(24.069147509221049367)*e**2-(21.549990225248066582)*e**3")

    def test_tbubble_with_weight1(self):
        self.do_test("e12|23|3|e|:0_1_1|2_1|1|0|",
                     "-3.0-(3.0)*e**(-1)-(3.311654539582639764)*e**2-(7.6217394743351143255)*e**3+e**(-2)-(0.6370242568726971373)*e")

    def test_tbubble_with_weight2(self):
        self.do_test("e12|23|3|e|:0_1_1|1_1|2|0|",
                     "4.5-(2.5)*e**(-1)+(8.292851526664017019)*e**2+(13.759548533622894061)*e**3+(6.3185121284363485687)*e+(0.5)*e**(-2)")

    def do_test(self, graph_as_string, expected_value_string):
        g = graph_util.graph_from_str(graph_as_string)
        unsubstituted_actual = reductor.calculate(g, weight_extractor=lambda e: e.weight)
        if not expected_value_string:
            self.assertIsNone(unsubstituted_actual)
            return
        expected = symbolic_functions.evaluate_expression(expected_value_string)
        actual = unsubstituted_actual.evaluate(substitute_sectors=True,
                                               _d=symbolic_functions.d_phi4,
                                               series_n=4,
                                               remove_o=True)
        actual = actual.normal().expand()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10E-6, self)


if __name__ == "__main__":
    unittest.main()
