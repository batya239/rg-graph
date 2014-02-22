#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from rggraphenv import storage, theory, symbolic_functions, StorageSettings, g_graph_calculator
import phi4

phi4.Configure()\
        .with_k_operation(phi4.MSKOperation())\
        .with_ir_filter(phi4.IRRelevanceCondition(phi4.SPACE_DIM_PHI4))\
        .with_uv_filter(phi4.UVRelevanceCondition(phi4.SPACE_DIM_PHI4))\
        .with_dimension(phi4.DIM_PHI4)\
        .with_calculators(g_graph_calculator.GLoopCalculator(phi4.DIM_PHI4))\
        .with_storage_holder(StorageSettings("phi4", "my_method_name", "my_description_to_method").on_shutdown(revert=True)).configure()

r_operator = phi4.ROperation()

g = phi4.graph_util.graph_from_str("e11|e|", do_init_weight=True)
r_star = r_operator.kr_star(g)
print r_star

#
# On exit from your script yuo shouldn't invoke any close/dispose method for any object like graph_calculator, storage
# It will be executed automatically
#