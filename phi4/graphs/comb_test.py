#!/usr/bin/python
# -*- coding: utf8

import comb
import unittest


class TestComb(unittest.TestCase):
    def testCombinations(self):
        xcomb = comb.xCombinations
        self.assertEqual(list(xcomb([1, 2, 3], 4)), [])
        self.assertEqual(list(xcomb(('1', 2), 1)), [('1',), (2,)])
        self.assertEqual(list(xcomb([1, 2, 3], 2)),
                         [[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]])

    def testPermutations(self):
        xperm = comb.xPermutations
        self.assertEqual(list(xperm([])), [[]])
        self.assertEqual(list(xperm(('1',))), [('1',)])
        self.assertEqual(list(xperm('ab')), ['ab', 'ba'])
        perm3 = [[1, 2, 3], [1, 3, 2],
                 [2, 1, 3], [2, 3, 1],
                 [3, 1, 2], [3, 2, 1]]
        self.assertEqual(list(xperm([1, 2, 3])), perm3)
        for p in xperm([1, 2, 3]):
            self.assertEqual(p, perm3.pop(0))


if __name__ == "__main__":
    unittest.main()

