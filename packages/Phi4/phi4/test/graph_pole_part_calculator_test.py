__author__ = 'dima'

import unittest
import graph_util
import graph_pole_part_calculator
import base_test_case
from rggraphenv import symbolic_functions


class GraphPolePartCalculatorTest(base_test_case.GraphStorageAwareTestCase):
    EPS = 10E-6

    def test_dotted_watermelon(self):
        self.do_test("e112|e2||", "(-1/2)*e**(-2)+1/2*e**(-1)")

    def do_test(self, graph_as_srt, expected_pole_part_as_str):
        g = graph_util.graph_from_str(graph_as_srt, do_init_weight=True)
        pole = graph_pole_part_calculator.calculate_graph_pole_part(g)
        actual = pole.convert_to_poly(no_order=True)
        expected = symbolic_functions.evaluate(expected_pole_part_as_str)
        symbolic_functions.check_series_equal_numerically(actual,
                                                          expected,
                                                          symbolic_functions.e,
                                                          GraphPolePartCalculatorTest.EPS,
                                                          self)

if __name__ == '__main__':
    unittest.main()