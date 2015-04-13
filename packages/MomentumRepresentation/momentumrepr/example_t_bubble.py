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





configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).\
    with_target_loops_count(2).\
    with_maximum_points_number(1000000).\
    with_absolute_error(10e-7).\
    with_relative_error(10e-7).\
    with_debug(True).configure()



graph_state_str = "e12|23|3|e|:0a_Aa_Aa|Aa|Aa|Aa|0A|::::"
print kr1.kr1_d_iw(graph_state_str, integration_operation=cuba_integration.cuba_integrate)


