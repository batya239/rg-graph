#!/usr/bin/python
# -*- coding: utf8
import unittest
import symbolic_functions

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(unittest.TestCase):
    def testExpansion(self):
        symbolic_functions.evaluate('G(1, 1)', (1, -1))


if __name__ == "__main__":
    unittest.main()

