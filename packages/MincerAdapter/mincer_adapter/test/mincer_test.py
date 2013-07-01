#!/usr/bin/python
# -*- coding: utf8
import os
import shutil
import unittest
import gfunctions
import graph_state
import graphine
import mincer

__author__ = 'daddy-bear'


class MincerTest(unittest.TestCase):
    def setUp(self):
        mincer.initMincer()

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

