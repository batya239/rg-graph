#!/usr/bin/python
# -*- coding: utf8
import unittest
import graphine
import diff_util

__author__ = 'dimas'


class DiffUtilTest(unittest.TestCase):
    def test_e112_23_33_e_(self):
        self.do_p2_diff_test("e112-23-33-e-", "[(-(-2+e)**(-1)*e, e112-23-34-e4--::), (-2*(-2+e)**(-1), e112-34-3-45-e5--:00000000-0000-oi-0000-00io--:), (-(-2+e)**(-1)*e, e112-23-44-4-e-::)]")

    def test_e112_22_e_(self):
        self.do_p2_diff_test("e112-22-e-", '[(-(-2+e)**(-1)*e, e112-33-3-e-::)]')

    def do_p2_diff_test(self, graph_state, expected_string):
        actual = diff_util.diff_p2(graphine.Graph.fromStr(graph_state))
        self.assertEqual(str(actual), expected_string)


if __name__ == "__main__":
    unittest.main()


