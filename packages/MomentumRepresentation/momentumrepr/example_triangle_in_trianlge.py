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


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).with_debug(True).configure()


def kr11(operation, graph_state_as_str):
    answer = zeroDict()
    for integrand in operation(graph_state_as_str):
        for d, a in cuba_integration.cuba_integrate(*integrand).items():
            answer[d] += a
    return answer

graph_state_str = "e12|e3|34|4|e|:0A_aA_aA|00_aA|aA_aA|aA|00|::::"
print kr11(kr1.kr1_log_divergence, graph_state_str)