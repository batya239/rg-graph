#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import r2
import itertools
import diff_util
import common
import graphine
import configure
import numerators_util
import ir_uv
import const
import graph_util2
import sys
import gfun_calculator
import momentum
import gfun_calculator
import sys
from rggraphenv import StorageSettings, StoragesHolder, g_graph_calculator, symbolic_functions


def main():
    configure.Configure() \
        .with_k_operation(common.MSKOperation()) \
        .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_dimension(const.DIM_PHI4) \
        .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4),
                          numerators_util.create_calculator(2, 3, 4)) \
        .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()


    g = graph_util2.graph_from_str(sys.argv[1])
    gfun_calculator.calculate_graph_value(g)

    StoragesHolder.instance().close()
    configure.Configure.clear()

if __name__ == "__main__":
    main()