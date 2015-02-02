#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import configure_mr
import kr1
import cuba_integration
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(900000).\
    with_absolute_error(10e-9).\
    with_relative_error(10e-9).\
    with_integration_algorithm("vegas").\
    with_debug(True).configure()


def kr11(operation, graph_state_as_str):
    answer = zeroDict()
    for integrand in operation(graph_state_as_str):
        for d, a in cuba_integration.cuba_integrate(*integrand).items():
            answer[d] += a
    return answer

# first diagram
graph_state_str = "e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|:::"
# second diagram
# graph_state_str = "e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|:::"
print kr11(kr1.kr1_d_iw, graph_state_str)