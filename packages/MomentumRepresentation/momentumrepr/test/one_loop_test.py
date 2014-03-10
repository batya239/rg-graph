#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import unittest
import configure_mr
import graph_util_mr
import kr1
import propagator
import cuba_integration
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict


class OneLoopTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configure_mr.Configure().\
            with_dimension(symbolic_functions.d_percolation).\
            with_target_loops_count(2).\
            with_debug(False).\
            with_delete_integration_tmp_dir_on_shutdown(True).\
            configure()

    def test_triangle(self):
        res = self.kr1(kr1.kr1_log_divergence, "e12|e2|e|:0A_aA_aA|00_aA|00|:::")
        self.assertTrue(abs(res[0] - 0.125) < 1E-3, res[0])
        self.assertTrue(abs(res[1] + 0.0625) < 1E-4, res[1])

    def test_bubble_d_iw(self):
        res = self.kr1(kr1.kr1_d_iw, "e11|e|:0A_aA_aA|00|:::")
        self.assertTrue(abs(res[0] - 0.125) < 1E-3, res)
        self.assertTrue(abs(res[1] + 0.0625) < 1E-4, res)

    def test_bubble_d_p2(self):
        graph_state_str = "e11|e|:0A_aA_aA|00|:::"
        res = self.kr1(kr1.kr1_d_p2, graph_state_str)
        self.assertTrue(abs(res[0] + 0.0625) < 1E-3, res)
        self.assertTrue(abs(res[1] - 0.03125) < 1E-5, res)

    def kr1(self, operation, graph_state_as_str):
        return operation(graph_state_as_str, integration_operation=cuba_integration.cuba_integrate)


if __name__ == "__main__":
    unittest.main()
