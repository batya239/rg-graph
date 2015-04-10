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
    with_maximum_points_number(1300000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-10).\
    with_integration_algorithm("suave").\
    with_debug(True).configure()

# g = graph_util_mr.from_str_alpha("e12|e3|34|4|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|0a|:::::")
# print integration.integrate(g, "log")
# {0: -0.0111299458087675+/-2.877601825e-07}

# g = graph_util_mr.from_str_alpha("e12|e3|34|4|e|:0A_aA_aA|0a_aA|aA_aA|aA|0a|:::::")
# print integration.integrate(g, "log")
# {0: 0.02012006289966+/-6.83725747429863e-07}

# g = graph_util_mr.from_str_alpha("e12|e3|e4|44||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa||:::::")
# print integration.integrate(g, "log")
# {0: -0.00141816006265125+/-7.732505875e-08}

# g = graph_util_mr.from_str_alpha("e12|e3|e4|44||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA||:::::")
# print integration.integrate(g, "log")
# {0: -0.01396626593407+/-3.0783802892725134e-07}

# g = graph_util_mr.from_str_alpha("e12|e3|34|4|e|:0A_aA_aA|0a_aA|Aa_aA|aA|0a|:::::")
# print integration.integrate(g, "log")
# {0: 0.00213990263272+/-4.3903675e-07}

# g = graph_util_mr.from_str_alpha("e12|e3|34|4||:0A_aA_aA|0a_Aa|aA_aA|aA|0a|:::::")
# print integration.integrate(g, "log")
# {0: 0.0021402780153475+/-1.0887136648165847e-06}

# g = graph_util_mr.from_str_alpha("e12|34|34|e|e|:0A_aA_aA|aA_aA|aA_aA|0a|0a|:::::")
# print integration.integrate(g, "log")
# {0: 0.0539410296824+/-1.36415323e-06}

# g = graph_util_mr.from_str_alpha("e12|34|34|e|e|:0A_aA_aA|aA_aA|Aa_aA|0a|0a|:::::")
# print integration.integrate(g, "log")
# TODO sign {0: 0.01798016026694+/-5.24144665e-07}

# g = graph_util_mr.from_str_alpha("e12|e3|33||:0A_aA_aA|0a_Aa|aA_aA||:::::")
# print integration.integrate(g, "iw")
# {0: -0.013966293988525+/-4.167598025e-07}

# g = graph_util_mr.from_str_alpha("e12|e3|33||:0A_aA_aA|0a_Aa|aA_aA||:::::")
# print integration.integrate(g, "p2")
# {0: 0.00591741842948755+/-1.259606525e-07}

# g = graph_util_mr.from_str_alpha("e12|23|3|e|:0A_aA_aA|aA_aA|aA|0a|:::::")
# print integration.integrate(g, "iw")
# {0: 0.0222595495641325+/-1.249830585e-06}

# g = graph_util_mr.from_str_alpha("e12|23|3|e|:0A_aA_aA|aA_aA|aA|0a|:::::")
# print integration.integrate(g, "p2")
# {0: -0.00923895347609+/-6.924922075e-07}

# g = graph_util_mr.from_str_alpha("e15|23|34|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|:::::")
# print integration.integrate(g, "iw")
# {0: -7.215709162e-05+/-1.6204245125e-06}}


# g = graph_util_mr.from_str_alpha("e15|23|34|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|:::::")
# print integration.integrate(g, "iw")
# {0: -7.215709162e-05+/-1.6204245125e-06}}


g = graph_util_mr.from_str_alpha("e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|:::::")
print integration.integrate(g, "iw")

# graphs = list()
# graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|")
# graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|")
# graphs.append("e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|23|4|e5|55||:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|23|4|e5|55||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|23|4|e5|55||:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|e|55||:0A_aA_aA|aA_Aa|aA_aA|0a|Aa_Aa||")
# graphs.append("e12|e3|34|5|55||:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA||")
# graphs.append("e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
# graphs.append("e12|e3|45|45|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")
# graphs = map(lambda g: g + ":::::", graphs)
#
# log = open("3l2t.log", "w")
# log.write("start\n")
#
# for g in graphs:
#     log.write(g + "\n")
#     print "START", g
#     try:
#         g = graph_util_mr.from_str_alpha(g)
#         result = integration.integrate(g, "iw")
#         log.write(str(result) + "\n")
#     except Exception as e:
#         print "FAIL"
#         log.write("FAIL" + "\n")
# log.close()
#

print "total time = %s" % (time.time() - t)
