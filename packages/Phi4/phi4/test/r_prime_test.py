#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import graphine
import common
import mincer_graph_calculator
from rggraphenv import graph_calculator
import r
import symbolic_functions
import base_test_case


__author__ = 'daddy-bear'


class RPrimeTestCase(base_test_case.GraphStorageAwareTestCase):
    def testIR(self):
        self.assertFalse(common.defaultGraphHasNotIRDivergence(graphine.Graph.fromStr("e123-224-4-4-e-")))
        irFree = [x for x in graphine.momentum.xPassExternalMomentum(graphine.Graph.fromStr("e112-e3-e34-44-e-"),
                                                         common.defaultGraphHasNotIRDivergenceFilter)]
        print irFree

    def test1LoopDiagramPRime(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("1/e"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testEyeRPrime(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e112-2-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("1/(2*e) - 1/(2*e**2)"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testSomeDiagram(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e13-23-33-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("2/(3*e) - 1/(2*e**2) + 1/(6*e**3)"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testE111_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e111-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("-1/(4*e*p**2)"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testE11_22_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-22-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("-1/e**2"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testE112_22_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e112-22-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("-1/(12*e*p**2) + 1/(6*e**2*p**2)"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testE11_22_33_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-22-33-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("1/e**3"),
                          r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter))

    def testE11_23_E33__(self):
        self.doTestRPrime("e11-23-e33--::", "-1/(2*e**2) + 1/(2*e**3)")

    def testE13_E22_33__(self):
        self.doTestRPrime("e13-e22-33--::", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    def testE112_E3_33__(self):
        self.doTestRPrime("e112-3-e33--::", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    def testE13_E23_33__(self):
        self.doTestRPrime("e13-e23-33--::", "2/(3*e) - 1/(2*e**2) + 1/(6*e**3)")

    #4 LOOPS

    def testE113_22_33_E_(self):
        self.doTestRPrime("e113-22-33-e-::", "5/(32*e*p**2) + 1/(16*e**2*p**2) - 1/(8*e**3*p**2)")

    def testE12_E3_333__(self):
        self.doTestRPrime("e12-e3-333--::", "-3/(8*e) + 1/(6*e**2)")

    def testE11_22_33_44_E_(self):
        self.doTestRPrime("e11-22-33-44-e-::", "-1/(e**4)")

    def testE11_22_34_E44_(self):
        self.doTestRPrime("e11-22-34-e44-::", "1/(2*e**3) - 1/(2*e**4)")

    def testE112_2_34_44_E_(self):
        self.doTestRPrime("e112-2-34-44-e-::", "-1/(4*e**2) + 1/(2*e**3) - 1/(4*e**4)")

    def testE11_24_E33_44__(self):
        self.doTestRPrime("e11-24-e33-44--::", "1/(3*e**2) + 1/(3*e**3) - 1/(3*e**4)")

    def testE11_23_E34_44__(self):
        self.doTestRPrime("e11-23-e34-44--::", "-2/(3*e**2) + 1/(2*e**3) - 1/(6*e**4)")

    def testE144_223_3_4_E_(self):
        self.doTestRPrime("e112-3-e34-44--::", "-1/(8*e**4)+1/(3*e**3)-5/(24*e**2)-1/(3*e)")

    def testE112_E4_33_44__(self):
        self.doTestRPrime("e112-4-e33-44--::", "-1/(4*e**4) + 1/(4*e**3) + 1/(4*e**2) + 1/(4*e) - zeta(3)/(2*e)")

    def testE12_E4_334_44__(self):
        self.doTestRPrime("e12-e4-334-44--::", "-7/(24*e) + 1/(4*e**2) - 1/(12*e**3)")

    def testE14_E24_333_4__(self):
        self.doTestRPrime("e14-e24-333-4--::", "-121/(192*e) + 11/(32*e**2) - 1/(16*e**3)")

    def testE14_E22_33_44__(self):
        self.doTestRPrime("e14-e22-33-44--::", "(-1/(4*e**4))*(1 - e - e**2 - e**3 + 2*zeta(3)*e**3)")

    def testE14_E22_3_444__(self):
        self.doTestRPrime("e14-e22-3-444--::", "37/(192*e) + 5/(32*e**2) - 5/(48*e**3)")

    def testE13_E22_34_44__(self):
        self.doTestRPrime("e13-e22-34-44--::", "-1/(8*e**4) + 1/(3*e**3)-5/(24*e**2)-1/(3*e**3)")

    def testE12_E24_33_44__(self):
        self.doTestRPrime("e12-e24-33-44--::", "(-1/(12*e**4))*(1 - 3*e + e**2 + 5*e**3 - 6*zeta(3)*e**3)")

    #WITH GRAPH CALCULATOR
    def testE12_223_3_E_(self):
        self.doTestRPrime("e12-223-3-e-::", "1/(3*e) - 2/(3*e**2) + 1/(3*e**3)", useGraphCalculator=True)

    def doTestRPrime(self, graphStateAsString, expectedResultAsString, useGraphCalculator=False):
        try:
            if useGraphCalculator:
                graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
            g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(graphStateAsString)))
            expected = symbolic_functions.evaluateForTests(expectedResultAsString)
            actual = r.KR1(g, common.MSKOperation(), common.defaultSubgraphUVFilter,
                           useGraphCalculator=useGraphCalculator)
            sub = (expected - actual).simplify()
            self.assertTrue(expected == actual or abs(
                (sub * symbolic_functions.e ** 5).evalf(subs={symbolic_functions.e: 1})) < 1e-100,
                            "\nactual = " + str(actual) + "\nexpected = " + str(expected) + "\nsub = " + str(sub))
        finally:
            graph_calculator.dispose()


if __name__ == "__main__":
    unittest.main()