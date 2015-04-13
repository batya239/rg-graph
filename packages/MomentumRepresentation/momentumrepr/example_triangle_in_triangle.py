#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import configure_mr
import kr1
import cuba_integration
from rggraphenv import symbolic_functions


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(2).\
    with_maximum_points_number(300000).\
    with_absolute_error(10e-8).\
    with_relative_error(10e-8).\
    with_debug(True).configure()


graph_state_str = "e12|e3|34|4|e|:0A_aA_aA|0a_aA|aA_aA|aA|0a|::::"
print kr1.kr1_log_divergence(graph_state_str, integration_operation=cuba_integration.cuba_integrate)
