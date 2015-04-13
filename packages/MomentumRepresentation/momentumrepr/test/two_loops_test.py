#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import unittest
import configure_mr
import graph_util_mr
import kr1
import propagator
import cuba_integration
import inject
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict


class TwoLoopsTest(unittest.TestCase):

    def setUp(self):
        configure_mr.Configure().\
            with_dimension(symbolic_functions.d_percolation).\
            with_target_loops_count(2).\
            with_debug(True).\
            with_absolute_error(10e-10).\
            with_relative_error(10e-10).\
            with_maximum_points_number(1200000).\
            with_delete_integration_tmp_dir_on_shutdown(True).\
            configure()

    def tearDown(self):
        inject.clear()

    def test_triangle_in_triangle(self):
        res = self.kr1(kr1.kr1_log_divergence, "e12|e3|34|4|e|:0A_aA_aA|0a_aA|aA_aA|aA|0a|::::")
        self.assertTrue(abs(res[0] - 0.020120) < 1E-3, res[0])

    def test_bubble_in_triangle(self):
        res = self.kr1(kr1.kr1_log_divergence, "e12|e3|e4|44||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa||::::")
        self.assertTrue(abs(res[0] + 0.0014) < 1E-3, res[0])

    def test_bubble_in_triangle1(self):
        res = self.kr1(kr1.kr1_log_divergence, "e12|e3|e4|44||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA||::::")
        self.assertTrue(abs(res[0] + 0.0014) < 1E-3, res[0])

    def test_bubble_in_triangle2(self):
        res = self.kr1(kr1.kr1_log_divergence, "e12|e3|e4|44||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA||::::")
        self.assertTrue(abs(res[0] + 0.014) < 1E-3, res[0])

    def test_tbubble_iw(self):
        res = self.kr1(kr1.kr1_d_iw, "e12|23|3|e|:0A_aA_aA|aA_aA|aA|00|::::")
        self.assertTrue(abs(res[0] - 0.0222) < 1E-3, res[0])

    # def test_tbubble_p2(self):
    #     res = self.kr1(kr1.kr1_d_p2, "e12|23|3|e|:0A_aA_aA|aA_aA|aA|00|::::")
    #     self.assertTrue(abs(res[0] + 0.00923) < 1E-4, res[0])
    #
    # def test_bubble_in_bubble_p2(self):
    #     res = self.kr1(kr1.kr1_d_p2, "e12|e3|33||:0A_aA_aA|0a_Aa|aA_aA||::::")
    #     self.assertTrue(abs(res[0] - 0.0059174) < 1E-4, res[0])

    def kr1(self, operation, graph_state_as_str):
        return operation(graph_state_as_str, integration_operation=cuba_integration.cuba_integrate)


if __name__ == "__main__":
    unittest.main()
