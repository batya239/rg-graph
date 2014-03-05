#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import unittest
import configure
import graph_util
import kr1
import propagator
import representation
from rggraphenv import symbolic_functions


class Kr1Test(unittest.TestCase):

    def setUp(self):
        configure.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).configure()

    def tearDown(self):
        configure.Configure.clear()

    def test_tbubble(self):
        graph_state_str = "e12|23|3|e|:0A_aA_aA|aA_aA|aA|0a|::::"
        print kr1.kr1_d_iw(graph_state_str)
        assert False

    def test_bubble(self):
        graph_state_str = "e11|e|:0A_aA_aA|00|::::"
        print kr1.kr1_log_divergence(graph_state_str)
        assert False

    def test_bubble_d_iw(self):
        graph_state_str = "e11|e|:0A_aA_aA|00|::::"
        print kr1.kr1_d_iw(graph_state_str)
        assert False

    def test_bubble_d_p2(self):
        graph_state_str = "e11|e|:0A_aA_aA|00|::::"
        print kr1.kr1_d_p2(graph_state_str)
        assert False

if __name__ == "__main__":
    unittest.main()
