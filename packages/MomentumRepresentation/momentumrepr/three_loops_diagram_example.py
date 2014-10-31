#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import unittest
import configure_mr
import graph_util_mr
import kr1
import propagator
import cuba_integration
from ipcluster_run import run
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict
from time import time


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
    with_integration_algorithm("vegas").\
    with_maximum_points_number("20000000000LL").\
    with_absolute_error(10e-12).\
    with_relative_error(10e-12).\
    with_debug(True).configure()


t = time()

graph_state_str = "e15|23|34|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|:::"
# print kr11(kr1.kr1_d_iw, graph_state_str)
print run(kr1.kr1_d_iw, graph_state_str)

print "Total time: %s sec" % (time() - t)
