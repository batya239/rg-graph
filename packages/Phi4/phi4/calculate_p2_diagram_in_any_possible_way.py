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

r.ROperation.set_debug(True)


def kr_star_quadratic_divergence(r_operator, graph):
    diff = diff_util.diff_p2(graph)
    result = list()

    i = -1
    for c, g in diff:
        i += 1
        if i != 1:
            continue
        _all = [x for x in graphine.momentum.xArbitrarilyPassMomentum(g)]
        _all.sort(key=common.graph_can_be_calculated_over_n_loops)
        r_star_values = list()
        r_star_graphs = list()
        for _g in _all:
            if "e112|33|e4|45|56|6||" not in str(_g):
                continue
            try:
                if common.graph_has_not_ir_divergence(_g):
                    r_star_values.append(r_operator.kr1(_g))
                else:
                    r_star_values.append(r_operator.kr_star(_g))
                r_star_graphs.append(_g)
            except common.CannotBeCalculatedError:
                pass
        print "Graph:", g
        print "Coefficient", c
        print "R_stars:\n"
        for v, g in zip(r_star_values, r_star_graphs):
            print "\t", v
            print "\t", v.subs(symbolic_functions.p == 1).evalf().expand().evalf().normal().expand()
            print "\t for", g
            print ""
        print "----"
        result.append(map(lambda v: c * v, r_star_values))


    # q = result[0][0] + result[2][0]

    # print "\n\n\n"
    # for r in result[1]:
    #     print (q + r).series(symbolic_functions.e == 0, 0).subs(symbolic_functions.p == 1).evalf().expand().evalf().normal().expand()


def main():
    configure.Configure() \
        .with_k_operation(common.MSKOperation()) \
        .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_dimension(const.DIM_PHI4) \
        .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4),
                           numerators_util.create_calculator(2)) \
        .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()

    operator = r.ROperation()
    g = graph_util.graph_from_str("e112|23|44|e44||", do_init_weight=True)
    kr_star_quadratic_divergence(operator, g)

    StoragesHolder.instance().close()
    configure.Configure.clear()

if __name__ == "__main__":
    main()


