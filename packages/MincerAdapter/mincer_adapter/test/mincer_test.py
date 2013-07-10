#!/usr/bin/python
# -*- coding: utf8
import unittest
import gfunctions
import graphine
import mincer

__author__ = 'daddy-bear'


class MincerTest(unittest.TestCase):
    def setUp(self):
        mincer.initMincer()

    def testLoop(self):
        self.doTest("e11-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", None)

    def testEye(self):
        self.doTest("e112-2-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", 
                    ("-21*e**3*zeta(5) - 9*e**3*zeta(3) - pi**4*e**3/20 + 81*e**3/2 - pi**4*e**2/20 - 3*e**2*zeta(3) + 27*e**2/2 - 3*e*zeta(3) + 9*e/2 + 3/2 + 1/(2*e) + 1/(2*e**2)", (2, -2)))

    def testTBubble(self):
        self.doTest("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", "-84*e**3*zeta(5)/p**2 - 18*e**3*zeta(3)**2/p**2 + 2*pi**6*e**3/(21*p**2) - pi**4*e**2/(5*p**2) + 42*e**2*zeta(5)/p**2 - 12*e*zeta(3)/p**2 + pi**4*e/(10*p**2) + 6*zeta(3)/p**2")

    def testTBubble1(self):
        self.doTest("e12-223-3-e-::['(0, 0)', '(1, 0)', '(1, 0)','(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", "0")

    def testTBubbleWithWeight(self):
        self.doTest("e12-23-3-e-::['(0, 0)', '(2, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
                    "-27*e**3*zeta(3)/p**4 - 3*pi**4*e**3/(20*p**4) - 9*e**3/(2*p**4) + 63*e**3*zeta(5)/p**4 - 9*e**2*zeta(3)/p**4 + 9*e**2/(2*p**4) + 3*pi**4*e**2/(20*p**4) - 9*e/(2*p**4) + 9*e*zeta(3)/p**4 + 9/(2*p**4) - 5/(2*e*p**4) + 1/(2*e**2*p**4)")
        self.doTest("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(2, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
                    "-126*e**3*zeta(5)/p**4 - 18*e**3*zeta(3)/p**4 + 57*e**3/p**4 + 9*pi**4*e**3/(10*p**4) - 39*e**2/p**4 - 3*pi**4*e**2/(10*p**4) + 54*e**2*zeta(3)/p**4 - 18*e*zeta(3)/p**4 + 21*e/p**4 - 3/p**4 - 3/(e*p**4) + 1/(e**2*p**4)")

    def testE122233e(self):
        self.doTest("e12-223-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
                    "0")

    def doTest(self, graphStr, expectedResult):
        epsPartAsString = expectedResult[0]
        graph = graphine.Graph.fromStr(graphStr)
        if not mincer.isApplicable(graph):
            self.assertIsNone(epsPartAsString)
            return
        actual = mincer.calculateGraph(graph)
        if expectedResult is None:
            self.assertIsNone(actual)
            return
        expected = gfunctions.symbolic_functions.evaluateForTests(epsPartAsString)
        sub = (expected - actual[0]).simplify()
        self.assertTrue(expected == actual[0] or abs(
            (sub * gfunctions.symbolic_functions._e ** 5).evalf(subs={gfunctions.symbolic_functions._e: 1})) < 1e-100,
                        "\nactual = " + str(actual[0]) + "\nexpected = " + str(expected) + "\nsub = " + str(sub))
        self.assertEquals(expectedResult[1], actual[1])

    def assertIsNone(self, arg):
        self.assertEquals(None, arg)

    def tearDown(self):
        mincer.disposeMincer()

if __name__ == "__main__":
    unittest.main()

