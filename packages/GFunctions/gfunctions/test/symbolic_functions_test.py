#!/usr/bin/python
# -*- coding: utf8
import unittest
import symbolic_functions

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def testExpansion(self):
        expansion = symbolic_functions.evaluateExpansion('G(1, 1)', (1, -1))
        self.assertEquals(set(str(expansion).split(" + ")), set(
            "1/e + 2*log(p) + 2*e*log(p)**2 + 4*e**2*log(p)**3/3 + 2*e**3*log(p)**4/3 + 4*e**4*log(p)**5/15 + 4*e**5*log(p)**6/45 + O(e**6)".split(
                " + ")))


if __name__ == "__main__":
    unittest.main()

