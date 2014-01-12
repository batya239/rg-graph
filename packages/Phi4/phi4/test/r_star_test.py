#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import swiginac
import graphine
import rggraphenv.graph_calculator
import base_test_case
import common
import r
import forest
from rggraphenv import symbolic_functions
import reduction
import graph_util

__author__ = 'daddy-bear'

r.DEBUG = True
forest.DEBUG = True

EPS = swiginac.numeric(1e-5)


class RStarTestCase(base_test_case.GraphStorageAwareTestCase):
    def test_e12_e234_33_4__(self):
        self._do_test_krstar("e12|e234|33|4||", "(11./6-zeta(3))/2/e-13./3./4/e**2+10./3/8/e**3-4./3/16/e**4")

    def _test_e112_e3_e34_44_e_(self):
        self._do_test_krstar("e112|e3|e34|44|e|", "0")

    def _test_e112_23_33_e_(self):
        self._do_test_krstar("112|e23|e33||", "-2./3/2/e+2./3/4/e**2-2./3/8/e**3")

    def test_e112_e2__(self):
        self._do_test_krstar("e112|e2||", "1/(2*e)-1/(2*e**2)")

    def test_e112_e33_3__(self):
        self._do_test_krstar("e112|e33|3||", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    def test_e112_e3_33__(self):
        self._do_test_krstar("e112|e3|33||", "1/(3*e**3)-1/(3*e**2)-1/(3*e)")

    def test_e112_23_e3__(self):
        self._do_test_krstar("e112|23|e3||", "1/(6*e**3)-1/(2*e**2)+2/(3*e)")

    def test_e12_e223_3__(self):
        self._do_test_krstar("e12|e223|3||", "1/(3*e**3)-2/(3*e**2)+1/(3*e)")

    def test_e1123_e23___(self):
        self._do_test_krstar("e1123|e23|||", "1/(3*e**3)-2/(3*e**2)+1/(3*e)")

    def test_e112_e3_334_4__(self):
        self._do_test_krstar("e112|e3|334|4||",
                             "-5/(24*e**4)+5/(12*e**3)+1/(24*e**2)-1/(4*e)",
                             use_graph_calculator=True)

    def test_e1123_44_4_4_e_(self):
        self._do_test_krstar("e1123|44|4|4|e|", "-1/(6*e**4)+1/(3*e**3)+1/(3*e**2)-1/e+zeta(3)/e")

    def test_e122_e33_4_44__(self):
        self._do_test_krstar("e112|e3|e44|e44||", "(0.5-zeta(3))/2/e+1./2/2/e**2+2./2/2/2/e**3-4./2/2/2/2/e**4")

    def test_e123_224_4_4_e_(self):
        self._do_test_krstar("e123|224|4|4|e|", "-1/(12*e**4)+1/(3*e**3)-5/(12*e**2)-1/(2*e)+zeta(3)/e",
                             use_graph_calculator=True)

    def test_e114_22_33_e4__(self):
        self._do_test_krstar("e114|22|33|e4||", "-1/(4*e**4)+1/(4*e**3)+1/(4*e**2)+1/(4*e)-zeta(3)/(2*e)")

    def test_e123_e23_33__(self):
        self._do_test_krstar("ee12|e34|334|4|e|",
                             "(5./2-2*zeta(3))/2/e-19./6/2/2/e**2+2./2/2/2/e**3-2./3/2/2/2/2/e**4",
                             use_graph_calculator=True)

    def test_ee12_233_34_4_ee_(self):
        self._do_test_krstar("ee12|233|34|4|ee|",
                             "-1/2*e**(-1)*(-1.8333333333333332593+zeta(3))-(1.0833333333333332593)*e**(-2)+(0.41666666666666668517)*e**(-3)-(0.08333333333333332871)*e**(-4)",
                             use_graph_calculator=True)

    def test_e112_23_e4_e45_55_e_(self):
        self._do_test_krstar("e112|23|e4|e45|55|e|",
                             "(8./30)/e-(8./60)/e/e+34./120/e/e/e-16./80/e/e/e/e+8./160/e/e/e/e/e",
                             use_graph_calculator=True)

    def test_112_e23_e4_45_55__(self):
        self._do_test_krstar("e112|23|e4|e45|55|e|",
                             "(8./30)/e-(8./60)/e/e+34./120/e/e/e-16./80/e/e/e/e+8./160/e/e/e/e/e",
                             use_graph_calculator=True)

    def test_ee12_23_33__(self):
        self._do_test_ir_coperation("ee12|23|33|", "2/3*e**(-1)-1/2*e**(-2)+1/6*e**(-3)")

    def test_ee12_223_4_e45_55_e_(self):
        self._do_test_krstar("ee12|223|4|e45|55|e|",
                             "-(0.53333333333333332593)*e**(-1)+(0.35833333333333333703)*e**(-3)+(0.11666666666666666852)*e**(-2)-(0.28333333333333332593)*e**(-4)+(0.074999999999999997224)*e**(-5)")

    def test_ee12_223_4_e45_55_e_2(self):
        self._do_test_krstar("e112|23|e4|445|5||",
                             "-(0.53333333333333332593)*e**(-1)+(0.35833333333333333703)*e**(-3)+(0.11666666666666666852)*e**(-2)-(0.28333333333333332593)*e**(-4)+(0.074999999999999997224)*e**(-5)")

    def test_e1123_e34_445__5___(self):
        self._do_test_krstar("e1123|e34|445||5||",
                             "-2./15/2/e+(16./15)/2/2/e/e+8./5/2/2/2/e/e/e-32./5/2/2/2/2/e/e/e/e+64./15/2/2/2/2/2/e/e/e/e/e")

    def test_ee12_334_355_5_ee5__(self):
        self._do_test_krstar("ee12|334|355|5|ee5||",
                             "-(3./10*zeta(4)-11./5*zeta(3)+14./5)/2/e-(2./5*zeta(3)-29./15)/2/2/e/e+34./15/2/2/2/e/e/e-52./15/2/2/2/2/e/e/e/e+8./5/2/2/2/2/2/e/e/e/e/e", use_graph_calculator=True)

    def test_ee12_334_345_e_55_e_(self):
        self._do_test_krstar("ee12|334|345|e|55|e|",
                             "-(4./3)/2/e-(2./15)/2/2/e/e+11./5/2/2/2/e/e/e-32./15/2/2/2/2/e/e/e/e+4./5/2/2/2/2/2/e/e/e/e/e")

    def test_ee12_234_35_45_e5_e_(self):
        self._do_test_krstar("e112|34|e35|45|e5|e|",
                             "-1/378*(Pi**6-(75.6000000000000042)*zeta(3)**2-1890*zeta(5))*e**(-1)-zeta(5)*e**(-2)", use_graph_calculator=True)

    def _do_test_krstar(self, graph_state_as_string, expected_result_as_string, use_graph_calculator=False):
        try:
            if use_graph_calculator:
                rggraphenv.graph_calculator.addCalculator(reduction.TwoAndThreeReductionCalculator())
            g = graph_util.graph_from_str(graph_state_as_string, do_init_color=True)
            expected = symbolic_functions.evaluate(expected_result_as_string).evalf()
            actual = r.KRStar(g,
                              common.MSKOperation(),
                              common.defaultSubgraphUVFilter,
                              use_graph_calculator=use_graph_calculator)
            sub = (expected - actual).evalf().simplify_indexed()
            self.assertTrue(expected == actual.simplify_indexed() or swiginac.abs(
                (sub * symbolic_functions.e ** 5).subs(symbolic_functions.e == 1)).evalf().compare(EPS) < 0,
                            "\nactual = " + str(actual.simplify_indexed().evalf()) +
                            "\nexpected = " + str(expected) + "\nsub = " + str(sub.evalf()))
        finally:
            rggraphenv.graph_calculator.dispose()


    def _do_test_ir_coperation(self, graph_state_as_string, expected_result_as_string):
        pass
        #g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(graph_state_as_string)))
        #expected = symbolic_functions.evaluate(expected_result_as_string)
        #actual = r.Delta_IR(g, common.MSKOperation(), common.defaultSubgraphUVFilter)
        #actual = actual if isinstance(actual, int) else actual.simplify_indexed()
        #sub = (expected - actual).simplify_indexed()
        #self.assertTrue(expected == actual or swiginac.abs(
        #    (sub * symbolic_functions.e ** 5).subs(symbolic_functions.e == 1)).compare(EPS) < 0,
        #                "\nactual = " + str(actual) + "\nexpected = " + str(expected) + "\nsub = " + str(sub.evalf()))


if __name__ == "__main__":
    unittest.main()