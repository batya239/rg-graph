__author__ = 'dima'


import graph_util
import r
import ir_uv
import const
import time
import unittest
import configure
import common
import gfun_calculator
import numerators_util
from rggraphenv import g_graph_calculator, StorageSettings, StorageHolder, symbolic_functions


class RPrimeTestCase(unittest.TestCase):
    def setUp(self):
        gfun_calculator.DEBUG = False
        self.start_time = time.time()
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI3))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI3))\
            .with_dimension(const.DIM_PHI3)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI3))\
            .with_storage_holder(StorageSettings("phi3", "test", "test", test=True)).configure()
        self.operator = r.RStar()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StorageHolder.instance().close()
        configure.Configure.clear()

    def test_one_loop_diagram(self):
        self._do_test_r1("e11|e|", "-1/6/e")

    def test_e12_23_3_e_(self):
        self._do_test_r1("e12|23|3|e|", "1/12*e**(-2)+(-1/18)*e**(-1)")

    def _do_test_r1(self, graph_state_str, expected_result_as_string):
        g = graph_util.graph_from_str(graph_state_str, do_init_weight=True)
        expected = symbolic_functions.evaluate(expected_result_as_string)
        actual = self.operator.kr_star(g, all_possible=True).evaluate().subs(symbolic_functions.p2 == 1).simplify_indexed().expand()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)

if __name__ == "__main__":
    unittest.main()