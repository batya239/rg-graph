#!/usr/bin/python
# -*- coding: utf8
import unittest
import graphine
import diff_util
import graph_util

__author__ = 'dimas'


class DiffUtilTest(unittest.TestCase):
    def test_e112_23_33_e_(self):
        self.do_p2_diff_test("e112|23|33|e|",
                             ["e112|23|34|e4||:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)_(1, 0)|(0, 0)_(1, 0)||:",
                             "e112|34|3|45|e5||:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(1, 0)_(1, 0)|(0, 0)_(1, 0)||:0_0_0_0|0_0|>|0_0|0_<||",
                             "e112|23|44|4|e|:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(0, 0)|:"])

    def test_e112_22_e_(self):
        self.do_p2_diff_test("e112|22|e|", ['e112|33|3|e|:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(0, 0)|:'])

    def do_p2_diff_test(self, graph_state, expected_graph_strings):
        expected_graph_strings = set(expected_graph_strings)
        actual = diff_util.diff_p2(graph_util.graph_from_str(graph_state, do_init_color=True))
        actual_graph_strings = set(map(lambda p: str(p[1]), actual))
        self.assertEqual(actual_graph_strings, expected_graph_strings)


if __name__ == "__main__":
    unittest.main()


