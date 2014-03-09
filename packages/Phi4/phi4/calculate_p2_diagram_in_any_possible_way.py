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
from rggraphenv import StorageSettings, StoragesHolder, g_graph_calculator, symbolic_functions


def kr_star_quadratic_divergence(r_operator, graph):
    diff = diff_util.diff_p2(graph)
    result = list()
    for c, g in diff:
        _all = [x for x in graphine.momentum.xArbitrarilyPassMomentum(g)]
        _all.sort(key=common.graph_can_be_calculated_over_n_loops)
        r_star_values = list()
        for _g in _all:
            try:
                if common.graph_has_not_ir_divergence(_g):
                    r_star_values.append(r_operator.kr1(_g))
                else:
                    r_star_values.append(r_operator.kr_star(_g))
            except common.CannotBeCalculatedError:
                pass
        print "Graph:", g
        print "Coefficient", c
        print "R_stars:\n"
        for v in r_star_values:
            print "\t", v.subs(symbolic_functions.p == 1).evalf()
        print "----"
        result.append((c, r_star_values))

    print "\n\n\n"
    mul_result = map(lambda c, r_star_values: map(lambda r_star_value: c * r_star_value, r_star_values), result)
    for comb in itertools.product(*mul_result):
        print "Combination:", comb
        print "Result:", reduce(lambda s, r: s + r, comb, 0).normal().expand()
        print "----"


def main():
    configure.Configure() \
        .with_k_operation(common.MSKOperation()) \
        .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_dimension(const.DIM_PHI4) \
        .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4),
                          numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR) \
        .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()

    operator = r.ROperation()
    g = graph_util.graph_from_str(sys.argv[1], do_init_weight=True)
    kr_star_quadratic_divergence(operator, g)

    StoragesHolder.instance().close(revert=True)
    configure.Configure.clear()

if __name__ == "__main__":
    main()


