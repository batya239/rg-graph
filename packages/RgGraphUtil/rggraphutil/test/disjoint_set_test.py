#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import unittest
from disjoint_set import DisjointSet


class DisjointSetTest(unittest.TestCase):
    def testAdd(self):
        s = DisjointSet()
        s.union(1, 2)
        s.add(1)
        sets = s.get_sets()
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0], set([1, 2]))

    def testAdd2(self):
        s = DisjointSet()
        s.union(1, 2)
        s.add(3)
        sets = s.get_sets()
        self.assertEqual(len(sets), 2)
        for a_set in sets:
            if len(a_set) == 1:
                self.assertEqual(a_set, set([3]))
            elif len(a_set) == 2:
                self.assertEqual(a_set, set([1, 2]))
            else:
                self.fail()

    def testExcluded(self):
        s = DisjointSet(excluded_indices=set([4]))
        s.union(1, 2)
        s.add(3)
        s.union(4, 3)
        s.union(4, 2)
        sets = s.get_sets()
        self.assertEqual(len(sets), 2)
        for a_set in sets:
            if len(a_set) == 1:
                self.assertEqual(a_set, set([3]))
            elif len(a_set) == 2:
                self.assertEqual(a_set, set([1, 2]))
            else:
                self.fail()

if __name__ == "__main__":
    unittest.main()

