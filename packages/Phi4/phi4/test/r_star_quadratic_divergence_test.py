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
from rggraphenv import symbolic_functions

__author__ = 'dimas'


EPS = swiginac.numeric(1e-5)


r.DEBUG = True

class RStarQuadraticTestCase(base_test_case.GraphStorageAwareTestCase):
    #UNITL 5 LOOPS

    # def test_e112_22_e_(self):
    #     self.do_test_rstar_quadratic_divergence("e112|22|e|", "1/6*e**(-2)-1/12*e**(-1)")
    #
    # def test_e112_33_e33__(self):
    #     self.do_test_rstar_quadratic_divergence("e112|33|e33||", "5/(32*e)+1/(16*e**2)-1/(8*e**3)")
    #
    # def test_e112_e3_333__(self):
    #     self.do_test_rstar_quadratic_divergence("e112|e3|333||", "5/(32*e)-1/(32*e**2)")
    #
    # def test_e112_23_33_e__(self):
    #     r.DEBUG = True
    #     self.do_test_rstar_quadratic_divergence("e112|23|33|e|", "-1/(3*e)+1/(6*e**2)-1/(12*e**3)")
    #     r.DEBUG = False
    #
    # def test_e123_e23_33__(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e23|33||", "-13/(96*e)+7/(48*e**2)-1/(24*e**3)",
    #                                             use_graph_calculator=True)

    #5 LOOPS

    # def test_5loops_diagram(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e24|34|44||", "((1./5*zeta(3)-347./480)/2/e+(39./40)/4/e/e-1./2/8/e/e/e+2./15/16/e/e/e/e)",
    #                                             use_graph_calculator=True)

    def test_5loops_diagram2(self):
        self.do_test_rstar_quadratic_divergence("e112|34|334|4|e|", "((3./5*zeta(3)-331./480)/2/e+(77./120)/4/e/e-23./30/8/e/e/e+2./5/16/e/e/e/e)",
                                                use_graph_calculator=True)

    # def test_5loops_diagram3(self):
    #     self.do_test_rstar_quadratic_divergence("e123|e23|44|44||", "(-(6./5*zeta(3)-277./240)/2/e-(11./60)/4/e/e-7./15/8/e/e/e+4./15/16/e/e/e/e)",
    #                                             use_graph_calculator=True)
    #
    # def test_5loops_diagram4_with_four_loops_reduction(self):
    #     #this diagram can be calculated only using 4loops diagrams values
    #     self.do_test_rstar_quadratic_divergence("e123|234|34|4|e|", "(-(6./5*zeta(4)+3./5*zeta(3))/2/e+(12./5*zeta(3))/4/e/e)",
    #                                             use_graph_calculator=True)

    def do_test_rstar_quadratic_divergence(self, graph_state_as_str, expected_str, use_graph_calculator=False):
        if use_graph_calculator:
                rggraphenv.graph_calculator.addCalculator(numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)
        g = graph_util.graph_from_str(graph_state_as_str, do_init_color=True)
        actual = r.KRStar_quadratic_divergence(g, common.MS_K_OPERATION,
                                               common.DEFAULT_SUBGRAPH_UV_FILTER,
                                               description="test_quadratic_divergence",
                                               use_graph_calculator=use_graph_calculator).simplify_indexed()
        expected = symbolic_functions.evaluate(expected_str)
        sub = (actual - expected).simplify_indexed()

        self.assertTrue(expected == actual.simplify_indexed()
                        or swiginac.abs((sub * symbolic_functions.e ** 5).
                                        subs(symbolic_functions.e == 1)).compare(EPS) < 0,
                        "\nactual = " + str(actual.simplify_indexed()) +
                        "\nexpected = " + str(expected) + "\nsub = " + str(sub))
        rggraphenv.graph_calculator.dispose()


if __name__ == "__main__":
    unittest.main()