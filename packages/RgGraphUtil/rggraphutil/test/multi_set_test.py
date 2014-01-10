#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import unittest
from rg_graph_collections import MultiSet


class MultiSetTest(unittest.TestCase):
    def test_creation(self):
        s = MultiSet(1, 1, 2, 3)
        d = {1: 2, 2: 1, 3: 1}
        for e in s.iter_elements():
            d[e] -= 1
        for v in d.values():
            self.assertIs(v, 0)
        d = {1: 2, 2: 1, 3: 1}
        for e in s.iter_entries():
            self.assertIs(e[1], d[e[0]])

    def test_len(self):
        s = MultiSet(1, 1, 2, 3)
        self.assertIs(len(s), 4)

    def test_add(self):
        s = MultiSet(1)
        s.add(1)
        s.add(2)
        s.add(3)
        d = {1: 2, 2: 1, 3: 1}
        for e in s.iter_entries():
            self.assertIs(e[1], d[e[0]])

    def test_eq(self):
        s1 = MultiSet(1, 1, 2, 3)
        s2 = MultiSet(1)
        s2.add(1)
        s2.add(2)
        s2.add(3)
        self.assertEqual(s1, s2)
        self.assertEqual(hash(s1), hash(s2))

    def assertIs(self, a, b):
        self.assertTrue(a is b)

if __name__ == "__main__":
    unittest.main()
