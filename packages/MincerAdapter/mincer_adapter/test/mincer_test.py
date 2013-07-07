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
        self.assertRaises(NotImplementedError, self.doTest, "e11-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", "1/e")

    def testEye(self):
        self.doTest("e112-2-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", "-21*e**3*zeta(5) - 9*e**3*zeta(3) - pi**4*e**3/20 + 81*e**3/2 - pi**4*e**2/20 - 3*e**2*zeta(3) + 27*e**2/2 - 3*e*zeta(3) + 9*e/2 + 3/2 + 1/(2*e) + 1/(2*e**2)")

    def testTBubble(self):
        self.doTest("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", "0")

    def testTBubbleWithWeight(self):
        self.doTest("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(2, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", "0")

    def doTest(self, graphStr, expectedResultAsString):
        actual = mincer.calculateGraph(graphine.Graph.fromStr(graphStr))
        expected = gfunctions.symbolic_functions.evaluateForTests(expectedResultAsString)
        sub = (expected - actual).simplify()
        self.assertTrue(expected == actual or abs(
            (sub * gfunctions.symbolic_functions._e ** 5).evalf(subs={gfunctions.symbolic_functions._e: 1})) < 1e-100,
                        "\nactual = " + str(actual) + "\nexpected = " + str(expected) + "\nsub = " + str(sub))

    def tearDown(self):
        mincer.disposeMincer()

if __name__ == "__main__":
    unittest.main()

