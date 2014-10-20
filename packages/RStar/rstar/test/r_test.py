#!/usr/bin/python
# -*- coding: utf8

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
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4), numerators_util.create_calculator(2, 3))\
            .with_storage_holder(StorageSettings("phi4", "test", "test", test=True)).configure()
        self.operator = r.RStar()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StorageHolder.instance().close()
        configure.Configure.clear()

    def test_one_loop_diagram(self):
        self._do_test_r1("ee11|ee|", "1/e")

    def test_eye(self):
        self._do_test_r1("ee12|e22|e|", "1/(2*e) - 1/(2*e**2)")

    def test_ee12_223_3_ee_(self):
        self._do_test_r1("ee12|223|3|ee|", "1/3/e-2/3/e**2+1/3/e**3")

    def test_e11_22_e_(self):
        self._do_test_r1("e11|22|e|", "-1/e**2")

    def test_e11_22_33_e_(self):
        self._do_test_r1("ee11|22|33|ee|", "1/e**3")

    def test_e11_23_e33__(self):
        self._do_test_r1("ee11|23|e33|e|", "-1/(2*e**2) + 1/(2*e**3)")

    def test_e13_e22_33__(self):
        self._do_test_r1("ee12|e33|e33||", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    def test_e13_e23_33__(self):
        self._do_test_r1("ee12|e23|33|e|", "2/(3*e) - 1/(2*e**2) + 1/(6*e**3)")

    def test_e11_22_33_44_e_(self):
        self._do_test_r1("ee11|22|33|44|ee|", "-1/(e**4)")

    def test_p2_ir(self):
        self._do_test_r1("12|3|e333|e|", "-3/8/e+1/6/e**2")

    def test_p2_ir2(self):
        self._do_test_r1("ee12|ee3|333||", "-3/8/e+1/6/e**2")

    def test_ee11_22_34_e44_(self):
        self._do_test_r1("ee11|22|34|e44|e|", "1/(2*e**3) - 1/(2*e**4)")

    def test_e112_2_34_44_e_(self):
        self._do_test_r1("e112|2|34|44|e|", "-1/(4*e**2) + 1/(2*e**3) - 1/(4*e**4)")

    def test_e112_e3_e44_e44__(self):
        self._do_test_r1("e112|e3|e44|e44||", "(1-2*zeta(3))/(4*e)+1/(4*e**2)+1/(4*e**3)-1/(4*e**4)")

    def test_e11_24_e33_44__(self):
        self._do_test_r1("e11|24|e33|44||", "1/(3*e**2) + 1/(3*e**3) - 1/(3*e**4)")

    def test_e11_23_e34_44__(self):
        self._do_test_r1("e11|23|e34|44||", "-2/(3*e**2) + 1/(2*e**3) - 1/(6*e**4)")

    def test_e144_223_3_4_e_(self):
        self._do_test_r1("e112|3|e34|44||", "-1/(8*e**4)+1/(3*e**3)-5/(24*e**2)-1/(3*e)")

    def test_e112_e4_33_44__(self):
        self._do_test_r1("e112|4|e33|44||", "-1/(4*e**4) + 1/(4*e**3) + 1/(4*e**2) + 1/(4*e) - zeta(3)/(2*e)")

    def test_e12_e4_334_44__(self):
        self._do_test_r1("e12|e4|334|44||", "-7/(24*e) + 1/(4*e**2) - 1/(12*e**3)")

    def test_e14_e24_333_4__(self):
        self._do_test_r1("e14|e24|333|4||", "-121/(192*e) + 11/(32*e**2) - 1/(16*e**3)")

    def test_e14_e22_33_44__(self):
        self._do_test_r1("e14|e22|33|44||", "(-1/(4*e**4))*(1 - e - e**2 - e**3 + 2*zeta(3)*e**3)")

    def test_e14_e22_3_444__(self):
        self._do_test_r1("e14|e22|3|444||", "37/(192*e) + 5/(32*e**2) - 5/(48*e**3)")

    def test_e112_34_ee3_44_e_(self):
        self._do_test_r1("e112|34|ee3|44|e|", "-2./3/2/e-5./6/2/2/e**2+8./3/2/2/2/e**3-2./2/2/2/2/e**4")

    def test_e12_e24_33_44__(self):
        self._do_test_r1("e12|e24|33|44||", "(-1/(12*e**4))*(1-3*e+e**2+5*e**3-6*zeta(3)*e**3)")

    def test_e1123_3_e4_44___(self):
        self._do_test_r1("e1123|3|e4|44||", "-13/(36*e) + psi(2, 2)/(72*e) - psi(2, 1)/(72*e) - 5/(24*e**2) + 1/(3*e**3) - 1/(8*e**4)")

    def test_e1234_e2_3_44__(self):
        self._do_test_r1("e1234|e2|3|44||", "psi(2, 2)/(24*e) - psi(2, 1)/(24*e) + 7/(6*e) - 19/(24*e**2) + 1/(4*e**3) - 1/(24*e**4)")

    def test_e112_33_e3__(self):
        self._do_test_r1("e112|33|e3|e|", "1/3*e**(-3)-1/3*e**(-2)-1/3*e**(-1)")

    def test_e12_e234_33_4__(self):
        self._do_test_r1("e12|e234|33|4||", "(11./6-zeta(3))/2/e-13./3./4/e**2+10./3/8/e**3-4./3/16/e**4")

    def _test_e112_23_33_e_(self):
        self._do_test_r1("112|e23|e33||", "-2./3/2/e+2./3/4/e**2-2./3/8/e**3")

    def test_e112_e2__(self):
        self._do_test_r1("e112|e2||", "1/(2*e)-1/(2*e**2)")

    def test_e112_e3_33__(self):
        self._do_test_r1("e112|e3|33||", "1/(3*e**3)-1/(3*e**2)-1/(3*e)")

    def test_complex_ir(self):
        self._do_test_r1("ee12|ee3|344|44||", "(-1/12)*e**(-3)+1/4*e**(-2)+(-7/24)*e**(-1)")

    def test_e112_e33_3__(self):
        self._do_test_r1("e112|e3|33||", "1/(3*e**3)-1/(3*e**2)-1/(3*e)")

    def test_e112_23_e3__(self):
        self._do_test_r1("e112|23|e3||", "1/(6*e**3)-1/(2*e**2)+2/(3*e)")

    def test_e12_e223_3__(self):
        self._do_test_r1("e12|e223|3||", "1/(3*e**3)-2/(3*e**2)+1/(3*e)")

    def test_e1123_e23___(self):
        self._do_test_r1("e1123|e23|||", "1/(3*e**3)-2/(3*e**2)+1/(3*e)")

    def test_e1123_44_4_4_e_(self):
        self._do_test_r1("e1123|44|4|4|e|", "-1/(6*e**4)+1/(3*e**3)+1/(3*e**2)-1/e+zeta(3)/e")

    def test_e122_e33_4_44__(self):
        self._do_test_r1("e112|e3|e44|e44||", "(1-2*zeta(3))/(4*e)+1/(4*e**2)+1/(4*e**3)-1/(4*e**4)")

    def test_e114_22_33_e4__(self):
        self._do_test_r1("e114|22|33|e4||", "-1/(4*e**4)+1/(4*e**3)+1/(4*e**2)+1/(4*e)-zeta(3)/(2*e)")

    def test_e112_34_e34_e4_e_(self):
        self._do_test_r1("e112|34|e34|e4|e|", "-1/2*e**(-2)*zeta(3)+1/2*e**(-1)*(-(1/60)*Pi**4+3*zeta(3))")

    def _do_test_r1(self, graph_state_str, expected_result_as_string):
        g = graph_util.graph_from_str(graph_state_str, do_init_weight=True)
        expected = symbolic_functions.evaluate(expected_result_as_string)
        actual = self.operator.kr_star(g, all_possible=True).evaluate().simplify_indexed().expand()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)


class RPrimeWithReductionTestCase(unittest.TestCase):
    def setUp(self):
        gfun_calculator.DEBUG = False
        self.start_time = time.time()
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4),
                              numerators_util.create_calculator(2, 3, 4))\
            .with_storage_holder(StorageSettings("phi4", "test", "test", test=True)).configure()
        self.operator = r.RStar()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StorageHolder.instance().close()
        configure.Configure.clear()

    def test_complex_ir(self):
        self._do_test_r1("ee12|ee3|344|44||", "(-1/12)*e**(-3)+1/4*e**(-2)+(-7/24)*e**(-1)")

    def _do_test_r1(self, graph_state_str, expected_result_as_string):
        g = graph_util.graph_from_str(graph_state_str, do_init_weight=True)
        expected = symbolic_functions.evaluate(expected_result_as_string)
        actual = self.operator.kr_star(g, all_possible=True).evaluate().simplify_indexed().expand()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)


class RPrimeP2Divergence(unittest.TestCase):
    def setUp(self):
        gfun_calculator.DEBUG = False
        self.start_time = time.time()
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4))\
            .with_storage_holder(StorageSettings("phi4", "test", "test", test=True)).configure()
        self.operator = r.RStar()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StorageHolder.instance().close()
        configure.Configure.clear()

    def _do_test_r1(self, graph_state_str, expected_result_as_string):
        g = graph_util.graph_from_str(graph_state_str, do_init_weight=True)
        expected = symbolic_functions.evaluate(expected_result_as_string) * symbolic_functions.p2
        actual = self.operator.kr_star(g, all_possible=True).evaluate().simplify_indexed().expand()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)

    def test_e111_e_(self):
        self._do_test_r1("e111|e|", "-1/4/e")

    def test_e112_22_e_(self):
        self._do_test_r1("e112|22|e|", "-1/12/e+1/6/e**2")

    def test_e112_33_e33_(self):
        self._do_test_r1("e112|33|e33|", "5/32/e+1/16/e**2-1/8/e**3")

    def test_e112_e3_333__(self):
        self._do_test_r1("e112|e3|333||", "5/32/e-1/32/e**2")

    def test_e123_e23_33__(self):
        self._do_test_r1("e123|e23|33||", "-13/96/e+7/48/e**2-1/24/e**3")

    def test_e112_23_33_e_(self):
        self._do_test_r1("e112|23|33|e|", "-1/e/3 + 1/6/e**2 - 1/12/e**3")

    def test_e112_33_e44_44__(self):
        self._do_test_r1("e112|33|e44|44||", "(1/5*zeta(3)-13/80)/e-1/8/e**2-1/20/e**3+1/10/e**4")

    def test_e112_23_e4_444__(self):
        self._do_test_r1("e112|23|e4|444||", "7/128/e - 23/240/e/e + 11/480/e/e/e")

    # def test_e123_e45_444_555___(self):
    #     self._do_test_r1("e123|e45|444|555|||", "(-1/192)*e**(-3)+(5/192)*e**(-2)+(-11/384)*e**(-1)")
    #
    # def test_8loop_watermelon(self):
    #     self._do_test_r1("e234|e567|555|666|777||||", "0")

    # def test_e112_33_e33__(self):
    #     self.do_test_rstar_quadratic_divergence("e112|33|e33||", "5/(32*e)+1/(16*e**2)-1/(8*e**3)")




if __name__ == "__main__":
    unittest.main()