#!/usr/bin/python
# -*- coding: utf8
import unittest
import time
import swiginac
import graph_state
import graphine
import common
from rggraphenv import g_graph_calculator, StoragesHolder, StorageSettings, symbolic_functions
import r
import base_test_case
import reduction
import graph_util
import configure
import ir_uv
import const
import numerators_util


__author__ = 'daddy-bear'

r.DEBUG = True

EPS = swiginac.numeric(1e-4)


class RPrimeTestCase(unittest.TestCase):
    def setUp(self):
        self.start_time = time.time()
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4))\
            .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()
        self.operator = r.ROperation()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StoragesHolder.instance().close(revert=True)
        configure.Configure.clear()

    def test_one_loop_diagram(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e11|e|")))
        self.assertEquals(symbolic_functions.evaluate("1/e"), self.operator.kr1(g).simplify_indexed())

    def test_eye(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e112|2|e|")))
        self.assertEquals(symbolic_functions.evaluate("1/(2*e) - 1/(2*e**2)"), self.operator.kr1(g).simplify_indexed())

    def test_some_diagram(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e13|23|33|e|")))
        self.assertEquals(symbolic_functions.evaluate("2/(3*e) - 1/(2*e**2) + 1/(6*e**3)"), self.operator.kr1(g).simplify_indexed())

    def test_e111_e_(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e111|e|")))
        self.assertEquals(symbolic_functions.evaluate("-p**2/(4*e)"), self.operator.kr1(g).simplify_indexed())

    def test_e11_22_e_(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e11|22|e|")))
        self.assertEquals(symbolic_functions.evaluate("-1/e**2"), self.operator.kr1(g).simplify_indexed())

    def test_e112_22_e_(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e112|22|e|")))
        self.assertEquals(symbolic_functions.evaluate("-1*p**2/(12*e) + p**2/(6*e**2)"), self.operator.kr1(g).simplify_indexed())

    def test_e11_22_33_e_(self):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr("e11|22|33|e|")))
        self.assertEquals(symbolic_functions.evaluate("1/e**3"), self.operator.kr1(g).simplify_indexed())

    def test_e11_23_e33__(self):
        self.do_test_r1("e11|23|e33||::", "-1/(2*e**2) + 1/(2*e**3)")

    def test_e13_e22_33__(self):
        self.do_test_r1("e13|e22|33||::", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    def test_e112_e3_33__(self):
        self.do_test_r1("e112|3|e33||::", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    def test_e13_e23_33__(self):
        self.do_test_r1("e13|e23|33||::", "2/(3*e) - 1/(2*e**2) + 1/(6*e**3)")

    ####4 LOOPS

    def test_e113_22_33_e_(self):
        self.do_test_r1("e113|22|33|e|::", "5*p**2/(32*e) + 1*p**2/(16*e**2) - 1*p**2/(8*e**3)")

    def test_e12_e3_333__(self):
        self.do_test_r1("e12|e3|333||::", "-3/(8*e) + 1/(6*e**2)")

    def test_e11_22_33_44_e_(self):
        self.do_test_r1("e11|22|33|44|e|::", "-1/(e**4)")

    def test_e11_22_34_e44_(self):
        self.do_test_r1("e11|22|34|e44|::", "1/(2*e**3) - 1/(2*e**4)")

    def test_e112_2_34_44_e_(self):
        self.do_test_r1("e112|2|34|44|e|::", "-1/(4*e**2) + 1/(2*e**3) - 1/(4*e**4)")

    def test_e112_e3_e44_e44__(self):
        self.do_test_r1("e112|e3|e44|e44||::", "((0.5-zeta(3))/2/e+1./2/2/e**2+2./2/2/2/e**3-4./2/2/2/2/e**4)")

    def test_e11_24_e33_44__(self):
        self.do_test_r1("e11|24|e33|44||::", "1/(3*e**2) + 1/(3*e**3) - 1/(3*e**4)")

    def test_e11_23_e34_44__(self):
        self.do_test_r1("e11|23|e34|44||::", "-2/(3*e**2) + 1/(2*e**3) - 1/(6*e**4)")

    def test_e144_223_3_4_e_(self):
        self.do_test_r1("e112|3|e34|44||::", "-1/(8*e**4)+1/(3*e**3)-5/(24*e**2)-1/(3*e)")

    def test_e112_e4_33_44__(self):
        self.do_test_r1("e112|4|e33|44||::", "-1/(4*e**4) + 1/(4*e**3) + 1/(4*e**2) + 1/(4*e) - zeta(3)/(2*e)")

    def test_e12_e4_334_44__(self):
        self.do_test_r1("e12|e4|334|44||::", "-7/(24*e) + 1/(4*e**2) - 1/(12*e**3)")

    def test_e14_e24_333_4__(self):
        self.do_test_r1("e14|e24|333|4||::", "-121/(192*e) + 11/(32*e**2) - 1/(16*e**3)")

    def test_e14_e22_33_44__(self):
        self.do_test_r1("e14|e22|33|44||::", "(-1/(4*e**4))*(1 - e - e**2 - e**3 + 2*zeta(3)*e**3)")

    def test_e14_e22_3_444__(self):
        self.do_test_r1("e14|e22|3|444||::", "37/(192*e) + 5/(32*e**2) - 5/(48*e**3)")

    def test_e112_34_ee3_44_e_(self):
        self.do_test_r1("e112|34|ee3|44|e|", "-2./3/2/e-5./6/2/2/e**2+8./3/2/2/2/e**3-2./2/2/2/2/e**4")

    def test_e12_e24_33_44__(self):
        self.do_test_r1("e12|e24|33|44||::", "(-1/(12*e**4))*(1-3*e+e**2+5*e**3-6*zeta(3)*e**3)")

    def test_e112_e3_333__(self):
        self.do_test_r1("e112|e3|333||", "5*p**2/(32*e)-p**2/(32*e**2)")

    def test_e1123_3_e4_44___(self):
        self.do_test_r1("e1123|3|e4|44||", "-13/(36*e) + psi(2, 2)/(72*e) - psi(2, 1)/(72*e) - 5/(24*e**2) + 1/(3*e**3) - 1/(8*e**4)")

    def test_e1234_e2_3_44__(self):
        self.do_test_r1("e1234|e2|3|44||", "psi(2, 2)/(24*e) - psi(2, 1)/(24*e) + 7/(6*e) - 19/(24*e**2) + 1/(4*e**3) - 1/(24*e**4)")

    def test_e112_33_e3__(self):
        self.do_test_r1("e112|33|e3|e|", "1/3*e**(-3)-1/3*e**(-2)-1/3*e**(-1)")

    def do_test_r1(self, graph_state_str, expected_result_as_string):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr(graph_state_str)))
        expected = symbolic_functions.evaluate(expected_result_as_string)
        actual = self.operator.kr1(g).simplify_indexed()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)


class RPrimeWithCalculatorTestCase(unittest.TestCase):

    def test_e12_223_3_e_(self):
        self.do_test_r1("e12|223|3|e|", "1/(3*e) - 2/(3*e**2) + 1/(3*e**3)")

    def test_e123_e23_33__(self):
        self.do_test_r1("e123|e23|33||", "-13*p**2/(96*e) + 7*p**2/(48*e**2) - 1*p**2/(24*e**3)")

    def test_e12_e23_33__(self):
        self.do_test_r1("e12|e23|33||", "1/(6*e**3) - 0.5/e**2 + 2/(3*e)")

    def test_e1123_2_e33__(self):
        self.do_test_r1("e1123|2|e33||", "p**2*(-1/(24*e**3) + 5/(48*e**2) + 1/(96*e))")

    def test_ee12_e23_334_4_e_(self):
        self.do_test_r1('ee12|e34|334|4|e|', "(5/2-2*zeta(3))/2/e-19/6/2/2/e**2+2/2/2/2/e**3-2/3/2/2/2/2/e**4")

    def test5loops(self):
        self.do_test_r1("ee12|e34|345|45|5|e|", "(-(23./5*zeta(5)-21./10*zeta(4)-5.*zeta(3))/2/e-(12./5*zeta(4)+36./5*zeta(3))/4/e/e+24./5*zeta(3)/8/e/e/e)")

    def setUp(self):
        self.start_time = time.time()
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4), numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)\
            .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()
        self.operator = r.ROperation()

    def tearDown(self):
        t = time.time() - self.start_time
        print "TIME - %s: %.3f" % (self.id(), t)
        StoragesHolder.instance().close(revert=True)
        configure.Configure.clear()

    def do_test_r1(self, graph_state_str, expected_result_as_string):
        g = graph_util.init_weight(graphine.Graph(graph_state.GraphState.fromStr(graph_state_str)))
        expected = symbolic_functions.evaluate(expected_result_as_string)
        actual = self.operator.kr1(g).simplify_indexed()
        symbolic_functions.check_series_equal_numerically(actual, expected, symbolic_functions.e, 10e-6, self)


if __name__ == "__main__":
    current_millis_time = lambda: int(round(time.time() * 1000))
    t = current_millis_time()
    unittest.main()
    print "TIME", t - current_millis_time()