#!/usr/bin/python
# -*- coding: utf8

import conserv
import unittest


class TestConserve(unittest.TestCase):
    def testGetNodesLines(self):
        testee = conserv.GetNodesLines
        self.assertEquals(
            sorted(testee({1: ('a', 3)})),
            sorted([set([1]), set([1])]))
        self.assertEquals(
            sorted(testee({1: ('a', 3), 2: (3, 4)})),
            sorted([set([1]), set([2]), set([1, 2])]))

    def testXConservations(self):
        testee = conserv.Conservations
        self.assertEquals(
            testee({1: ('a', 3), 2: (3, 4)}),
            set([frozenset([1]), frozenset([2]), frozenset([1, 2])]))
        self.assertTrue(
            frozenset([1, 3]) in testee({0: (-1, 0),
                                         1: (0, 1),
                                         2: (1, 2),
                                         3: (2, -2)}))


if __name__ == "__main__":
    unittest.main()

