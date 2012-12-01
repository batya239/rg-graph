#!/usr/bin/python
# -*- coding: utf8
import unittest
from multiindex import MultiIndex

mi = MultiIndex({1: 2, 3: 5, 5: 1})

class MultiIndexTestCase(unittest.TestCase):
    def testPrint(self):
        self.assertEquals(mi.__repr__(), '(x_1^2)(x_3^5)(x_5^1)')

    def testHasVar(self):
        self.assertTrue(mi.hasVar(3))
        self.assertFalse(mi.hasVar(2))

    def testSet1toVar(self):
        self.assertEquals(mi.set1toVar(2), MultiIndex({3: 5, 5: 1, 1: 2}))
        self.assertEquals(mi.set1toVar(1), MultiIndex({5: 1, 3: 5}))
        self.assertEquals(mi.set1toVar(3), MultiIndex({5: 1, 1: 2}))

    def testDiff(self):
        diff = mi.diff(3)
        self.assertEquals(diff[0], 5)
        self.assertEquals(diff[1].__repr__(), '(x_1^2)(x_3^4)(x_5^1)')
        diff = mi.diff(7)
        self.assertEquals(diff[0], 0)

    def testStretch(self):
        stretched = mi.stretch(1, [2, 3])
        self.assertEquals(stretched.__repr__(), '(x_1^7)(x_3^5)(x_5^1)')

    def testEmpty(self):
        empty = MultiIndex()
        self.assertEquals(empty.__repr__(), '1')

    if __name__ == "__main__":
        unittest.main()

