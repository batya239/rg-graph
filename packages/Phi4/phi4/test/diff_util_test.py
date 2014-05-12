#!/usr/bin/python
# -*- coding: utf8
import unittest
import graphine
import diff_util
import graph_util
import configure
import common
import ir_uv
import const
from rggraphenv import StoragesHolder, StorageSettings

__author__ = 'dimas'


class DiffUtilTest(unittest.TestCase):
    def setUp(self):
        configure.Configure() \
            .with_k_operation(common.MSKOperation()) \
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
            .with_dimension(const.DIM_PHI4) \
            .with_calculators() \
            .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()

    def tearDown(self):
        StoragesHolder.instance().close()
        configure.Configure.clear()

    def test_e112_23_33_e_(self):
        self.do_p2_diff_test("e112|23|33|e|",
                             ["e112|23|34|e4||:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)_(1, 0)|(0, 0)_(1, 0)||::",
                             "e112|34|3|45|e5||:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(1, 0)_(1, 0)|(0, 0)_(1, 0)||:0_0_0_0|0_0|>|0_0|0_<||:0_0_0_1|0_0|1|0_1|0_1||",
                             "e112|23|44|4|e|:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(0, 0)|::"])

    def test_e112_22_e_(self):
        self.do_p2_diff_test("e112|22|e|", ['e112|33|3|e|:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)|(0, 0)|::'])

    def do_p2_diff_test(self, graph_state, expected_graph_strings):
        expected_graph_strings = set(expected_graph_strings)
        actual = diff_util.diff_p2(graph_util.graph_from_str(graph_state, do_init_weight=True))
        actual_graph_strings = set(map(lambda p: str(p[1]), actual))
        self.assertEqual(actual_graph_strings, expected_graph_strings)


if __name__ == "__main__":
    unittest.main()


