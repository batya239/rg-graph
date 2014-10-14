#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import r
import itertools
import diff_util
import common
import graphine
import configure
import numerators_util
import ir_uv
import const
import graph_util
import sys
import gfun_calculator
import momentum
from rggraphenv import StorageSettings, StoragesHolder, g_graph_calculator, symbolic_functions

r.RStar.set_debug(True)


def kr_star(graph):
    _all = [x for x in momentum.arbitrarily_pass_momentum(graph)]
    result = list()
    for _g in _all:
        try:
            print "PERFORM", _g
            kr1 = r.RStar().kr_star(_g, False)
            result.append((_g, kr1))
            print "RESULT", kr1
        except common.CannotBeCalculatedError:
            print "exception"

    for g, v in result:
        print "------------"
        print "graph", g
        print "kr1", v


def main():
    configure.Configure() \
        .with_k_operation(common.MSKOperation()) \
        .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_dimension(const.DIM_PHI4) \
        .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4)) \
        .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()

    # g = graph_util2.graph_from_str("e112|e3|334|4||::::1_1_1_1_e", do_init_weight=True)
    # g = graph_util2.graph_from_str("e112|e3|4|444||::::1_1_e_1_1", do_init_weight=True)
    g = graph_util.graph_from_str("ee12|ee3|344|44||", do_init_weight=True)
    kr_star(g)

    StoragesHolder.instance().close()
    configure.Configure.clear()

if __name__ == "__main__":
    main()