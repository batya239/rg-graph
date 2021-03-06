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


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(100000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-8).\
    with_integration_algorithm("suave").\
    with_debug(True).configure()


graph_state_str = "e15|23|34|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|::::"
print kr1.kr1_d_iw(graph_state_str, integration_operation=cuba_integration.cuba_integrate)
