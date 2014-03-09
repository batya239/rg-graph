#!/usr/bin/python
# -*- coding: utf8

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


configure_mr.Configure()\
    .with_dimension(symbolic_functions.d_percolation)\
    .with_target_loops_count(3)\
    .with_debug(True)\
    .with_maximum_points_number(12000000)\
    .with_relative_error(10e-11)\
    .with_absolute_error(10e-11)\
    .configure()

result = []

graph_state_str = "e12|e3|34|4|e|:0A_aA_aA|00_aA|aA_aA|aA|00|::::"
result.append(kr1.kr1_log_divergence(graph_state_str, cuba_integration.cuba_integrate))

print result