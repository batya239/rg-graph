#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import graph_util_mr
import configure_mr
import integration
from rggraphenv import symbolic_functions

configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(5000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_integration_algorithm("vegas").\
    with_debug(True).configure()

g = graph_util_mr.from_str_alpha("e12|e3|33||:0A_aA_aA|0a_Aa|aA_aA||:::::")
print integration.integrate(g, "iw")

# g = graph_util_mr.from_str_alpha("e12|e2|e|:0A_aA_aA|0a_Aa|0a|:::::")
# print integration.integrate(g, "log")
