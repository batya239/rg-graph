#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import graphine
import r_prime
import symbolic_functions
import test

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(test.GraphStorageAwareTestCase):
    def test1LoopDiagramPRime(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("1/e"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testEyeRPrime(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e12-e22--::")))
        self.assertEquals(symbolic_functions.evaluateForTests("1/(2*e) - 1/(2*e**2)"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testSomeDiagram(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e13-23-33-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("2/(3*e) - 1/(2*e**2) + 1/(6*e**3)"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testE111_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e111-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("-1/(4*e*p**2)"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testE11_22_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-22-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("-1/e**2"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testE112_22_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e112-22-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("-1/(12*e*p**2) + 1/(6*e**2*p**2)"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testE11_22_33_E_(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-22-33-e-::")))
        self.assertEquals(symbolic_functions.evaluateForTests("1/e**3"), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

    def testE11_23_E33__(self):
        self.doTestRPrime("e11-23-e33--::", "-1/(2*e**2) + 1/(2*e**3)")

    #TODO
    def testE12_E3_333__(self):
        self.doTestRPrime("e12-e3-333--::", "1")

    def testE13_E22_33__(self):
        self.doTestRPrime("e13-e22-33--::", "-1/(3*e) - 1/(3*e**2) + 1/(3*e**3)")

    #TODO sympy, bad resolving of equals
    def testE112_E3_33__(self):
        self.doTestRPrime("e112-e3-33--::", "(log(p)**2 - log(p))/e - 1/(3*e) + log(p)/e**2 - 1/(3*e**2) + 1/(3*e**3)")

    def testE13_E23_33__(self):
        self.doTestRPrime("e13-e23-33--::", "2/(3*e) - 1/(2*e**2) + 1/(6*e**3)")

    #4 LOOPS

    def testE113_22_33_E_(self):
        self.doTestRPrime("e113-22-33-e-::", "5/(32*e*p**2) + 1/(16*e**2*p**2) - 1/(8*e**3*p**2)")

    #TODO wrong result
    def testE112_E3_333__(self):
        self.doTestRPrime("e112-e3-333--::", "1")

    def doTestRPrime(self, graphStateAsString, expectedResultAsString):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr(graphStateAsString)))
        self.assertEquals(symbolic_functions.evaluateForTests(expectedResultAsString), r_prime.doRPrime(g, r_prime.MSKOperation(), r_prime.defaultSubgraphUVFilter))

if __name__ == "__main__":
    unittest.main()