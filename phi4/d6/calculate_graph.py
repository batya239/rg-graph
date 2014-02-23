#!/usr/bin/python
# -*- coding: utf8


__author__ = 'mkompan'


import sys
from rggraphenv import storage, theory, symbolic_functions, StorageSettings, g_graph_calculator
import phi4
#from two_and_three_loop_d6 import reduction_calculator_3loop, reduction_calculator_2loop, reduction_calculator_23loop
from two_and_three_loop_d6 import reduction_calculator_2loop


SPACE_DIM_PHI3 = 6
DIM_PHI3 = 6-2*symbolic_functions.e
phi4.Configure()\
        .with_k_operation(phi4.MSKOperation())\
        .with_ir_filter(phi4.IRRelevanceCondition(SPACE_DIM_PHI3))\
        .with_uv_filter(phi4.UVRelevanceCondition(SPACE_DIM_PHI3))\
        .with_dimension(DIM_PHI3)\
        .with_calculators(g_graph_calculator.GLoopCalculator(DIM_PHI3), reduction_calculator_2loop)\
        .with_storage_holder(StorageSettings("phi3", "my_method_name", "my_description_to_method").on_shutdown(revert=True)).configure()

r_operator = phi4.ROperation()
r_operator.set_debug(True)

#g = phi4.graph_util.graph_from_str("e11|e|", do_init_weight=True)
#g = phi4.graph_util.graph_from_str("e12|e3|33||", do_init_weight=True)  #??
#g = phi4.graph_util.graph_from_str("e12|e2||", do_init_weight=True)
#g = phi4.graph_util.graph_from_str("e12|e3|34|4|e|", do_init_weight=True)
g = phi4.graph_util.graph_from_str("e12|e3|e4|44||", do_init_weight=True)
r_star = r_operator.kr_star(g)
print r_star


# print
# print r_operator.kr1(g)
#
# l = 2 - symbolic_functions.e
# G = symbolic_functions.G
# d = DIM_PHI3
# e = symbolic_functions.e
# series = symbolic_functions.series
# print G(1, 1, d)
# print series(G(1 + e, 1, d=d), e, 0, 0)
# print series(G(1, 1, d) * G(3 - l, 1, d=d), e, 0, 0).evalf()
# print series(G(1, 1, d) * G(3 - l, 1, d=d) - G(1, 1, d) * G(1, 1, d), e, 0, 0).evalf()