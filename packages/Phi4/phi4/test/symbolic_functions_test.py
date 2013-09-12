#!/usr/bin/python
# -*- coding: utf8
import unittest
import symbolic_functions

__author__ = 'daddy-bear'


class SymbolicFunctionsTestCase(unittest.TestCase):
    def testExpansion(self):
        actualExpression = symbolic_functions.evaluateSeries(symbolic_functions.g(1, 1), (1, -1))
        self.assertEquals(set(str(actualExpression).split(" + ")), set("1/e + O(1)".split(" + ")))


if __name__ == "__main__":
    unittest.main()

