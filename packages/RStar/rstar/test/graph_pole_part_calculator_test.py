
__author__ = 'dima'

import unittest
import graph_pole_part_calculator
import time
import configure
import graph_util
import ir_uv
import const
import common
from rggraphenv import symbolic_functions, g_graph_calculator, StorageSettings, StorageHolder


class GraphPolePartCalculatorTest(unittest.TestCase):
    EPS = 10E-6

    def setUp(self):
        self.start_time = time.time()
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4))\
            .with_storage_holder(StorageSettings("phi4", "test", "test", test=True)).configure()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StorageHolder.instance().close()
        configure.Configure.clear()

    def test_dotted_watermelon(self):
        self._do_test("e112|e2||", "2*e**(-1)*log(p)-1/2*e**(-2)+1/2*e**(-1)")

    def _do_test(self, graph_as_srt, expected_pole_part_as_str):
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