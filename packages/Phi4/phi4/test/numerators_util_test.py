__author__ = 'dima'


import numerators_util
import graphine
import swiginac
import base_test_case
import unittest
import rggraphenv
EPS = swiginac.numeric(1e-5)

numerators_util.DEBUG = True


class NumeratorUtilTestCase(base_test_case.GraphStorageAwareTestCase):

    def test1(self):
        g = graphine.Graph.fromStr("e112|2|e|:(777, 0)_(1, 0)_(2, 0)_(1, 0)|(1, 0)|(666, 0)|:00_00_oi_00|00|00|")
        rggraphenv.graph_calculator.addCalculator(numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)
        print numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR.calculate(g)[0].evalf()


if __name__ == "__main__":
    unittest.main()