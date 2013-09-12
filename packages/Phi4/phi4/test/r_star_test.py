#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import mincer_graph_calculator
import graphine
import rggraphenv.graph_calculator
import base_test_case
import common
import r
import symbolic_functions

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(base_test_case.GraphStorageAwareTestCase):
    def testE112_E3_33__(self):
        self.doTestKRStar("e112-e3-33--", "1/(3*e**3)-1/(3*e**2)-1/(3*e)")

    def testE112_23_E3__(self):
        self.doTestKRStar("e112-23-e3--", "1/(6*e**3)-1/(2*e**2)+2/(3*e)")

    def testE12_E223_3__(self):
        self.doTestKRStar("e12-e223-3--", "1/(3*e**3)-2/(3*e**2)+1/(3*e)")

    def testE1123_E23___(self):
        self.doTestKRStar("e1123-e23---", "1/(3*e**3)-2/(3*e**2)+1/(3*e)")

    def testE1234_E2_33_4__(self):
        self.doTestKRStar("e1234-e2-33-4--", "-1/(12*e**4)+5/(12*e**3)-13/(12*e**2)+(11-6*zeta(3))/(12*e)")

    def testE112_E3_334_4__(self):
        self.doTestKRStar("e112-e3-334-4--", "-5/(24*e**4)+5/(12*e**3)+1/(24*e**2)-1/(4*e)")

    def testE1123_44_4_4_E_(self):
        self.doTestKRStar("e1123-44-4-4-e-", "-1/(6*e**4)+1/(3*e**3)+1/(3*e**2)-1/e+zeta(3)/e")

    def testE122_E33_4_44__(self):
        self.doTestKRStar("e122-e33-4-44--", "-1/(4*e**4)+1/(4*e**3)+1/(4*e**2)+1/(4*e)-zeta(3)/(2*e)")

    def testE123_224_4_4_E_(self):
        self.doTestKRStar("e123-224-4-4-e-", "-1/(12*e**4)+1/(3*e**3)-5/(12*e**2)-1/(2*e)+zeta(3)/e",
                          useGraphCalculator=True)

    def testE114_22_33_E4__(self):
        self.doTestKRStar("e114-22-33-e4--", "-1/(4*e**4)+1/(4*e**3)+1/(4*e**2)+1/(4*e)-zeta(3)/(2*e)")

    def doTestKRStar(self, graphStateAsString, expectedResultAsString, useGraphCalculator=False):
        try:
            if useGraphCalculator:
                rggraphenv.graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
            g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(graphStateAsString)))
            expected = symbolic_functions.evaluateForTests(expectedResultAsString)
            actual = r.KRStar(g,  common.MSKOperation(), common.defaultSubgraphUVFilter, useGraphCalculator=useGraphCalculator)
            sub = (expected - actual).simplify()
            self.assertTrue(expected == actual or abs(
                (sub * symbolic_functions.e ** 5).evalf(subs={symbolic_functions.e: 1})) < 1e-100,
                            "\nactual = " + str(actual) + "\nexpected = " + str(expected) + "\nsub = " + str(sub))
        finally:
            rggraphenv.graph_calculator.dispose()


if __name__ == "__main__":
    unittest.main()