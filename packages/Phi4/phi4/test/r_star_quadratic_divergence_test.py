#!/usr/bin/python
# -*- coding: utf8
import graphine
import base_test_case
import common
import r
import swiginac
import unittest
import rggraphenv
import reduction
import numerators_util
import graph_util
import time
import configure
import ir_uv
import const
from rggraphenv import symbolic_functions, g_graph_calculator, StorageSettings, StoragesHolder

__author__ = 'dimas'


import gfun_calculator
gfun_calculator.DEBUG = True

EPS = swiginac.numeric(1e-5)


r.DEBUG = True


class RStarQuadraticTestCase(base_test_case.GraphStorageAwareTestCase):
    def setUp(self):
        self.start_time = time.time()
        configure.Configure() \
            .with_k_operation(common.MSKOperation()) \
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
            .with_dimension(const.DIM_PHI4) \
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4)) \
            .with_storage_holder(StorageSettings("phi4", "test", "test")).configure()
        self.operator = r.ROperation()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StoragesHolder.instance().close(revert=True)
        configure.Configure.clear()

    def test_e112_22_e_(self):
        self.do_test_rstar_quadratic_divergence("e112|22|e|", "1/6*e**(-2)-1/12*e**(-1)")

    def test_e112_33_e33__(self):
        self.do_test_rstar_quadratic_divergence("e112|33|e33||", "5/(32*e)+1/(16*e**2)-1/(8*e**3)")

    def test_e112_e3_333__(self):
        self.do_test_rstar_quadratic_divergence("e112|e3|333||", "5/(32*e)-1/(32*e**2)")

    def test_e112_23_33_e__(self):
        r.DEBUG = True
        self.do_test_rstar_quadratic_divergence("e112|23|33|e|", "-1/(3*e)+1/(6*e**2)-1/(12*e**3)")
        r.DEBUG = False

    # def test_e123_e23_33__(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e23|33||", "-13/(96*e)+7/(48*e**2)-1/(24*e**3)",
    #                                             use_graph_calculator=True)

    #5 LOOPS

    # def test_5loops_diagram(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e24|34|44||", "((1./5*zeta(3)-347./480)/2/e+(39./40)/4/e/e-1./2/8/e/e/e+2./15/16/e/e/e/e)",
    #                                             use_graph_calculator=True)

    # def test_5loops_diagram2(self):
    #     self.do_test_rstar_quadratic_divergence("e112|34|334|4|e|", "((3./5*zeta(3)-331./480)/2/e+(77./120)/4/e/e-23./30/8/e/e/e+2./5/16/e/e/e/e)",
    #                                             use_graph_calculator=True)

    # def test_5loops_diagram2(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e45|445|455|||", "e",
    #                                             use_graph_calculator=True)

    # def test_5loops_diagram3(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e23|44|44||", "(-(6./5*zeta(3)-277./240)/2/e-(11./60)/4/e/e-7./15/8/e/e/e+4./15/16/e/e/e/e)",
    #                                             use_graph_calculator=True)
    #
    # def test_5loops_diagram4_with_four_loops_reduction(self):
    #     #this diagram can be calculated only using 4loops diagrams values
    #     self.do_test_rstar_quadratic_divergence("e123|234|34|4|e|", "(-(6./5*zeta(4)+3./5*zeta(3))/2/e+(12./5*zeta(3))/4/e/e)",
    #                                             use_graph_calculator=True)

    def do_test_rstar_quadratic_divergence(self, graph_state_as_str, expected_str):
        g = graph_util.graph_from_str(graph_state_as_str, do_init_weight=True)
        actual = self.operator.kr_star_quadratic_divergence(g).simplify_indexed()
        expected = symbolic_functions.evaluate(expected_str)
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)


if __name__ == "__main__":
    unittest.main()