#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


from momentumrepr import graph_util_mr
from momentumrepr import configure_mr
from rggraphenv import symbolic_functions
import time

t = time.time()
configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.cln(2) * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(100000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_integration_algorithm("suave").\
    with_debug(True).configure()

g = graph_util_mr.from_str_alpha("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||:::::")
import cluster_runner

graphs = list()
# graphs.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||")
# graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|aA_Aa|0a|aA_aA||")
# graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|0a|aA_aA||")
# graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_aA|aA_Aa|0a|aA_aA||")
# graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_Aa|aA_aA|0a|Aa_Aa||")
# graphs.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|0A|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|aA_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|aA_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|Aa_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|Aa|0a_aA|Aa_Aa||")
# graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_Aa|aA|0a_Aa|aA_aA||")

# graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|:::::")
# graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|:::::")
# graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|:::::")
# graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|Aa|Aa|0A|:::::")
# graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|:::::")
# graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|:::::")
# graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|Aa_aA|0a_aA|0a_Aa|aA||:::::")
# graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_aA|Aa||:::::")
# graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_Aa|Aa||:::::")
# graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||:::::")
# graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_aA||:::::")
# graphs.append("e12|33|45|6|e6|e6||:0a_aA_Aa|aA_aA|Aa_aA|aA|0A_aA|0a_Aa||:::::")
# graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||:::::")
# graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||:::::")

# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|aA_aA|aA|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|Aa|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|Aa|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_aA|aA|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|aA|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|Aa_aA|aA|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|aA_aA|aA|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|aA|0a|:::::")
# graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_aA|aA|0a|:::::")
# graphs.append("e12|e3|e4|45|6|66||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||:::::")
# graphs.append("e12|e3|e4|45|6|66||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||:::::")
# graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|0a_Aa||:::::")
# graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_aA||:::::")
# graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_Aa||:::::")
# graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||:::::")
# graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|Aa_aA|0a|0a|:::::")
# graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA_aA|0a|0a|:::::")
# graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA_aA|0a|0a|:::::")
# graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_aA|0A|0a|:::::")
# graphs.append("e12|23|4|56|56|e|e|:0a_Aa_aA|aA_Aa|aA|Aa_aA|Aa_aA|0A|0a|:::::")
# graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_aA|Aa|Aa_aA|Aa_aA|0A|0a|:::::")
# graphs.append("e12|e3|e4|55|66|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||:::::")
# graphs.append("e12|e3|e4|55|66|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|aA|0a|:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|:::::")
# graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|:::::")




graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|aA|0a|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|aA_aA|aA|0a|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|Aa_aA|aA|0a|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|Aa_aA|aA|0a|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|aA_aA|aA|0a|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|Aa_aA|aA|0a|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|Aa_Aa|Aa|0A|:::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|Aa|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|Aa_aA|aA_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|Aa|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_aA|aA_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|:::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|Aa|aA|0a|:::::")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0a_Aa|0A_aA|Aa_Aa||:::::")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa|aA_aA||:::::")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_aA|Aa|0a_Aa|0A_aA|Aa_Aa||:::::")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_aA|aA_Aa|aA|0A_aA|0a_Aa|aA_aA||:::::")
graphs.append("e12|e3|e4|56|56|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||:::::")
graphs.append("e12|e3|e4|56|56|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|Aa|0A_aA|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|Aa|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_Aa|aA_aA|aA|0a_Aa|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_aA|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_aA|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_Aa|aA|0a_aA|aA|0a|:::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|aA|0A_aA|aA|0a|:::::")
graphs.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|:::::")
graphs.append("e12|e3|44|55|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|:::::")

for g in graphs:
    print cluster_runner.calculate_diagram(g, "", "~/.server", "~/.aggregator")