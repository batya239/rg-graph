#!/usr/bin/python
# -*- coding: utf8
import unittest
import symbolic_functions
import rggraphenv.computer_algebra as ca

__author__ = 'daddy-bear'


class SymbolicFunctionsTestCase(unittest.TestCase):
    def testExpansion(self):
        actualExpression = ca.series(symbolic_functions.evaluate("G(1, 1)", (1, -1)), ca.e, 0, 0)
        self.assertEquals(actualExpression, 1/ca.e)

    def testGWithNumerators(self):
        expr = symbolic_functions.evaluate("G1(2, 1)*G1(3-l*1, 1)*G2(1, 4-l*2)", (0, 0))
        pole = ca.series(expr, ca.e, 0, 0)
        self.assertEquals(pole, -1/(3*ca.e))

        expr = symbolic_functions.evaluate("G1(2, 1)*G2(1, 3-l*1)", (0, 0))
        pole = ca.series(expr, ca.e, 0, 0)
        self.assertEquals(pole, -1/(2*ca.e))

if __name__ == "__main__":
    unittest.main()

