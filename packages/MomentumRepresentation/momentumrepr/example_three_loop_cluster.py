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
import cluster_runner


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number("50000000000LL").\
    with_absolute_error(10e-10).\
    with_relative_error(10e-8).\
    with_integration_algorithm("vegas").\
    with_debug(True).configure()


graph_state_str = "e15|23|34|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|:::"
cluster_runner.calculate_diagram(graph_state_str, "w", "~/.server", "~/.aggregator")
