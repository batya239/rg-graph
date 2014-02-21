__author__ = 'dima'


import numerators_util
import graphine
import swiginac
import base_test_case
import unittest
import rggraphenv
import graph_util

numerators_util.DEBUG = True


class NumeratorUtilTestCase(base_test_case.GraphStorageAwareTestCase):
    def test1(self):
        g = graph_util.graph_from_str("e11|22|33|e|::0_>_0|0_0|0_>|0|:0_1_0|0_1|0_1|0|", do_init_weight=True)
        rggraphenv.graph_calculator.addCalculator(numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)
        res = numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR.calculate(g)
        self.assertEqual(str(res), "(1/4*e**(-3), (2, -3))")

    def test2(self):
        g = graph_util.graph_from_str("e11|22|33|e|::0_0_0|0_>|0_>|0|:0_1_0|0_1|0_1|0|", do_init_weight=True)
        rggraphenv.graph_calculator.addCalculator(numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)
        res = numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR.calculate(g)
        self.assertEqual(str(res), "(1/4*e**(-3), (2, -3))")

if __name__ == "__main__":
    unittest.main()