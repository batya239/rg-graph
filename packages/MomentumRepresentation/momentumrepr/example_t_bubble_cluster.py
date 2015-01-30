#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

from rggraphenv import symbolic_functions
from rggraphutil import zeroDict

import configure_mr
import kr1
import cluster_runner


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).\
    with_target_loops_count(3).\
    with_maximum_points_number(13000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_debug(True).configure()


graph_state_str = "e12|23|3|e|:0a_Aa_Aa|Aa|Aa|Aa|0A|:::"
cluster_runner.calculate_diagram(graph_state_str, "w", "~/.server", "~/.aggregator")