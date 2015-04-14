#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import graph_util_mr
import configure_mr
import integration
from rggraphenv import symbolic_functions
import time

t = time.time()
configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.cln(2) * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(10000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_integration_algorithm("suave").\
    with_debug(True).configure()

g = graph_util_mr.from_str_alpha("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||:::::")
import cluster_runner
print cluster_runner.calculate_diagram(g, "", "~/.server", "~/.aggregator")