#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import unittest
import configure_mr
import graph_util_mr
import kr1
import propagator
import representation
import swiginac_integration
import scipy_integration
import cuba_integration
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict


class Kr1Test(unittest.TestCase):

    def setUp(self):
        configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).with_debug(True).configure()

    def tearDown(self):
        configure_mr.Configure.clear()

    # def test_tbubble(self):
    #     graph_state_str = "e12|23|3|e|:0A_aA_aA|aA_aA|aA|0a|::::"
    #     print kr1.kr1_d_iw(graph_state_str)
    #     assert False


    # def test_bubble_in_bubble_p2(self):
    #     graph_state_str = "e12|e3|33||:0A_aA_aA|00_Aa|aA_aA||::::"
    #     print self.kr1(kr1.kr1_d_p2, graph_state_str)
    #     assert False
    #

    # def test_bubble_in_bubble_iw(self):
    #     graph_state_str = "e12|e3|33||:0A_aA_aA|00_Aa|aA_aA||::::"
    #     print self.kr1(kr1.kr1_d_iw, graph_state_str)
    #     assert False

    def test_triangle(self):
        graph_state_str = "e12|e2|e|:0A_aA_aA|00_aA|00|::::"
        res = self.kr1(kr1.kr1_log_divergence, graph_state_str)
        self.assertTrue(abs(res[0] - 0.125) < 1E-3, res[0])
        self.assertTrue(abs(res[1] + 0.0625) < 1E-4, res[1])

    def test_bubble_d_iw(self):
        graph_state_str = "e11|e|:0A_aA_aA|00|::::"
        res = self.kr1(kr1.kr1_d_iw, graph_state_str)
        self.assertTrue(abs(res[0] - 0.125) < 1E-3, res)
        self.assertTrue(abs(res[1] + 0.0625) < 1E-4, res)

    # def test_bubble_d_p2(self):
    #     graph_state_str = "e11|e|:0A_aA_aA|00|::::"
    #     res = self.kr1(kr1.kr1_d_p2, graph_state_str)
    #     self.assertTrue(abs(res[0] + 0.0625) < 1E-4, res)
    #     self.assertTrue(abs(res[1] - 0.03125) < 1E-5, res)

    def kr1(self, operation, graph_state_as_str):
        answer = zeroDict()
        for integrand in operation(graph_state_as_str):
            for d, a in cuba_integration.cuba_integrate(*integrand).items():
                answer[d] += a
        return answer


if __name__ == "__main__":
    unittest.main()