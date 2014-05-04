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
    with_target_loops_count(3).\
    with_maximum_points_number(13000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_debug(True).configure()


def kr11(operation, graph_state_as_str):
    answer = zeroDict()
    for integrand in operation(graph_state_as_str):
        for d, a in cuba_integration.cuba_integrate(*integrand).items():
            answer[d] += a
    return answer


graph_state_str = "e12|23|3|e|:0a_Aa_Aa|Aa|Aa|Aa|0A|:::"
print kr11(kr1.kr1_d_p2, graph_state_str)


