#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import graph_util_ms
import configure_mr
from rggraphenv import symbolic_functions
from integration import calculate


configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.CLN_TWO * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(6000000).\
    with_absolute_error(10e-11).\
    with_relative_error(10e-9).\
    with_integration_algorithm("suave").\
    with_debug(True).\
    with_delete_integration_tmp_dir_on_shutdown(False).configure()
# # # g = graph_util_ms.from_str("e12|e3|34|4|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|0a|::::")
# # # g = graph_util_ms.from_str("e12|e2|e|:0A_aA_aA|0a_Aa|0a|::::")
# # # g = graph_util_ms.from_str("e12|e3|e3||:0A_aA_aA|0a_Aa|0a_aA|::::")
# # g = graph_util_ms.from_str("e11|e|:0A_aA_aA|0a|::::")
# # # g = graph_util_ms.from_str("e12|e3|e4|44||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa||::::")
# # # g = graph_util_ms.from_str("e12|23|3|e|:0A_aA_aA|aA_aA|aA|0a|::::") # d1
# # g = graph_util_ms.from_str("e12|e3|e4|44||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa||::::")
# # # g = graph_util_ms.from_str("e12|e3|e4|44||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa||::::") #d3
# # # g = graph_util_ms.from_str("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||::::")
# # g = graph_util_ms.from_str("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||::::")
# # g = graph_util_ms.from_str("e12|34|34|e|e|:00_aA_aA|aA_aA|Aa_aA|00|00|::::")
# # g = graph_util_ms.from_str("e12|3|45|45|e|e|:00_aA_aA|aA|aA_aA|Aa_aA|00|00|::::")
# # g = graph_util_ms.from_str("e12|34|34|e|e|:00_aA_aA|aA_aA|Aa_aA|00|00|::::")
# # g = graph_util_ms.from_str("e12|3|45|45|e|e|:00_aA_aA|aA|aA_aA|Aa_aA|00|00|::::")
# # result = calculate(g, None, insert_p2_dotes=1)
#
#
#
#
# graphs p2
# g = graph_util_ms.from_str("e12|34|34|e|e|:00_aA_aA|aA_Aa|aA_aA|00|00|::::")  # 1
# g = graph_util_ms.from_str("e12|3|45|45|e|e|:00_aA_aA|aA|aA_aA|Aa_aA|00|00|::::")  # 2
# g = graph_util_ms.from_str("e123|e3|4|4|e|:00_aA_aA_aA|00_Aa|aA|Aa|00|::::")  # 3
# g = graph_util_ms.from_str("e12|34|35|e|e5||:00_aA_aA|aA_Aa|aA_aA|00|00_Aa||::::")  # 4

# g = graph_util_ms.from_str("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|::::")
g = graph_util_ms.from_str("e12|e3|33||:00_aA_aA|00_Aa|aA_aA||::::")
# g = graph_util_ms.from_str("e11|e|:00_aA_aA|00|::::")
# g = graph_util_ms.from_str("e12|e2||:00_aA_aA|00_Aa||::::")
# g = graph_util_ms.from_str("e12|23|3|e|:00_aA_aA|aA_aA|aA|00|::::")
# g = graph_util_ms.from_str("e12|3|3|e|:00_aA_aA|aA|aA|00|::::")
# g = graph_util_ms.from_str("e12|e3|3||:00_aA_aA|00_Aa|aA||::::")
# g = graph_util_ms.from_str("e12|e3|e4|44||:00_Aa_aA|00_aA|00_Aa|aA_aA||::::")
result = calculate(g, None)
print "RES", result
# # # RES defaultdict(<function <lambda> at 0x10d896398>, {-2: -0.01073181850492+/-9.757746033333332e-07, -3: -0.0039062503956583325+/-1.6870322e-07, -1: -0.0204877902347116+/-3.895274636080001e-06})
# # # # RES defaultdict(<function <lambda> at 0x108ef6398>, {-2: -0.010732024139191667+/-8.487505999999999e-08, -3: -0.003906252204265+/-1.4819028333333333e-08, -1: -0.020486770992769424+/-4.331757293854968e-07})
# # #
# # import spherical_coordinats
# # print configure_mr.Configure.dimension()
# # print 3
# # # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 2) * g11() ** 3/ (2*pi)**(3*configure_mr.Configure.dimension())).series(symbolic_functions.e == 0, 3).evalf()
# # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 1) * spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 1) * g11() ** 3/ (2*pi)**(3*configure_mr.Configure.dimension())).series(symbolic_functions.e == 0, 3).evalf()
# # print 2
# # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 1) * g11() ** 2/ (2*pi)**(2*configure_mr.Configure.dimension())).series(symbolic_functions.e == 0, 3).evalf()
# # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 1) * g11() ** 2/ (2*pi)**(2*configure_mr.Configure.dimension())).series(symbolic_functions.e == 0, 3)
# # print "loops", 1
# # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * g11() / (2*pi)**(configure_mr.Configure.dimension())).series(e==0, 3).evalf() #2+O(e)
# # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) * g11() / (2*pi)**(configure_mr.Configure.dimension())).series(e==0, 2).coeff(e).simplify_indexed() #2+O(e)
# # print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension()) / spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 1)).simplify_indexed()
# print (spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 1) / spherical_coordinats.sphere_square(configure_mr.Configure.dimension() - 2)).simplify_indexed()