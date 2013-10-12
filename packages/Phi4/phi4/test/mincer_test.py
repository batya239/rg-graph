#!/usr/bin/python
# -*- coding: utf8
import unittest
import graphine
import symbolic_functions
import mincer
import swiginac

__author__ = 'daddy-bear'


class MincerTest(unittest.TestCase):
    def setUp(self):
        mincer.init_mincer()

    #def testLoop(self):
    #    self.doTest("e11-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", (None,))
    #
    def testSome1(self):
        self.doTest("e112-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(2, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
                    ("(-0.5)*e**(-3)+4.25*e**(-2)+(-17.375)*e**(-1)", (2, -2)))

    #def testEye(self):
    #    self.doTest("e112-2-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
    #                (
    #                "-21*e**3*zeta(5) - 9*e**3*zeta(3) - pi**4*e**3/20 + 81*e**3/2 - pi**4*e**2/20 - 3*e**2*zeta(3) + 27*e**2/2 - 3*e*zeta(3) + 9*e/2 + 3/2 + 1/(2*e) + 1/(2*e**2)",
    #                (2, -2)))
    #
    #def testTBubble(self):
    #    self.doTest("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']", (
    #    "-84.0*e**3*zeta(5) - 18.0*e**3*zeta(3)**2 + 0.0952380952380952*pi**6*e**3 - 0.2*pi**4*e**2 + 42.0*e**2*zeta(5) - 12.0*e*zeta(3) + 0.1*pi**4*e + 6.0*zeta(3)",
    #    (3, -2)))
    #
    #def testTBubble1(self):
    #    self.doTest("e12-223-3-e-::['(0, 0)', '(1, 0)', '(1, 0)','(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
    #                "0")
    #
    #def testTBubbleWithWeight(self):
    #    self.doTest("e12-23-3-e-::['(0, 0)', '(2, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
    #                (
    #                "-27*e**3*zeta(3) - 3*pi**4*e**3/(20) - 9*e**3/(2) + 63*e**3*zeta(5) - 9*e**2*zeta(3) + 9*e**2/(2) + 3*pi**4*e**2/(20) - 9*e/(2) + 9*e*zeta(3) + 9/(2.) - 5/(2*e) + 1/(2*e**2)",
    #                (4, -2)))
    #    self.doTest("e12-23-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(2, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
    #                (
    #                "-126*e**3*zeta(5) - 18*e**3*zeta(3) + 57*e**3 + 9*pi**4*e**3/(10) - 39*e**2 - 3*pi**4*e**2/(10) + 54*e**2*zeta(3) - 18*e*zeta(3) + 21*e - 3 - 3/(e) + 1/(e**2)",
    #                (4, -2)))
    #
    #def testE12_223_3_E(self):
    #    self.doTest("e12-223-3-e-::['(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(0, 0)']",
    #                ("0", None))

    def doTest(self, graphStr, expectedResult):
        epsPartAsString = expectedResult[0]
        graph = graphine.Graph.fromStr(graphStr)
        if not mincer.is_applicable(graph):
            self.assertIsNone(epsPartAsString)
            return
        actual = mincer.calculate_graph(graph)
        if epsPartAsString is None:
            self.assertIsNone(actual)
            return
        self.assertIsNotNone(actual)
        expected = symbolic_functions.evaluate(epsPartAsString)
        sub = (expected - actual[0]).simplify_indexed()
        self.assertTrue(expected == actual[0] or swiginac.abs(
            sub.subs(symbolic_functions.e == 1)).compare(swiginac.numeric(1e-10)) < -1,
                        "\nactual = " + str(actual[0]) + "\nexpected = " + str(expected) + "\nsub = " + str(sub.evalf()))
        self.assertEquals(expectedResult[1], actual[1])

    def assertIsNone(self, arg):
        self.assertEquals(None, arg)

    def assertIsNotNone(self, arg):
        self.assertNotEquals(None, arg)

    def tearDown(self):
        mincer.dispose_mincer()


if __name__ == "__main__":
    unittest.main()