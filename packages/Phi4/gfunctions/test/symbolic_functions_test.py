#!/usr/bin/python
# -*- coding: utf8
import unittest
import symbolic_functions

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def testExpansion(self):
        expansion = symbolic_functions.evaluateSeries('G(1, 1)', (1, -1))
        self.assertEquals(set(str(expansion).split(" + ")), set("1/e + O(1)".split(" + ")))

if __name__ == "__main__":
    unittest.main()

