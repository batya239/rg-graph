#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import configure_mr
import kr1
import cuba_integration
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(2000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-9).\
    with_integration_algorithm("vegas").\
    with_debug(True).configure()

# graph_state_str = "e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|::::"
graph_state_str = "e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|0a|aA_aA||::::"
print kr1.kr1_log_divergence(graph_state_str, integration_operation=cuba_integration.cuba_integrate)