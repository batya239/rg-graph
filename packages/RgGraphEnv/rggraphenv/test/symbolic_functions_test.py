# !/usr/bin/python
# -*- coding: utf8
import unittest

import symbolic_functions


__author__ = 'daddy-bear'

e = symbolic_functions.e
symbolic_functions.l = symbolic_functions.d_phi4 / symbolic_functions.CLN_TWO - symbolic_functions.CLN_ONE


class SymbolicFunctionsTestCase(unittest.TestCase):
    def testExpansion(self):
        actualExpression = symbolic_functions.series(symbolic_functions.evaluate_expression("G(1, 1)"),
                                                     e, 0, 0,
                                                     remove_order=True)
        self.assertEquals(actualExpression, 1 / e)

    def testGWithNumerators1(self):
        expr = symbolic_functions.evaluate_expression("G1(2, 1)*G1(3-l*1, 1)*G2(1, 4-l*2)")
        pole = symbolic_functions.series(expr, e, 0, -1, remove_order=True)
        self.assertEquals(pole.evalf(), -1 / (3 * e))

    def testGWithNumerators2(self):
        expr = symbolic_functions.evaluate_expression("G1(2, 1)*G2(1, 3-l*1)")
        pole = symbolic_functions.series(expr, e, 0, 0, remove_order=True)
        self.assertEquals(pole, -1 / (2 * e))


if __name__ == "__main__":
    unittest.main()