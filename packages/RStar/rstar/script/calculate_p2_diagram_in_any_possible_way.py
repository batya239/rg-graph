#!/usr/bin/python
# -*- coding: utf8
from deprecated import r, graph_util

__author__ = 'dima'

import itertools
import diff_util
import common
import graphine
import momentum
import configure
import numerators_util
import ir_uv
import const
import sys
import graph_pole_part_calculator
from rggraphenv import StorageSettings, StoragesHolder, g_graph_calculator, symbolic_functions

r.ROperation.set_debug(True)


def kr_star_quadratic_divergence(r_operator, graph):
    diff = diff_util.diff_p2(graph)
    result = list()

    print "DIFF", diff
    # i = -1
    for c, g in diff:
        # i += 1
        # if i != 1:
        #     continue
        _all = [x for x in momentum.arbitrarily_pass_momentum(g)]
        _all.sort(key=common.graph_can_be_calculated_over_n_loops)
        r_star_values = list()
        r_star_graphs = list()
        for _g in _all:
            # if "e12|e34|35|66|556|6||:" not in str(_g):
            #     continue
            print "PERFORM", _g
            try:
                if common.graph_has_not_ir_divergence(_g):
                    r_star_values.append(r_operator.kr1(_g))
                else:
                    r_star_values.append(r_operator.kr_star(_g))
                r_star_graphs.append(_g)
                # break
            except common.CannotBeCalculatedError:
                pass
        print "Graph:", g
        print "Coefficient", c
        print "R_stars:\n"
        for v, g in zip(r_star_values, r_star_graphs):
            print "\t", v
            # print "kr1[%s] = %s" % (graph.getPresentableStr(), symbolic_functions.series(v * c, symbolic_functions.e, symbolic_functions.CLN_ZERO, 0, False))
            print "\t", v.subs(symbolic_functions.p == 1).evalf().expand().evalf().normal().expand()
            print "\t for", g
            print ""
        print "----"
        result.append(map(lambda v: c * v, r_star_values))


    if len(result) == 3:
        q = result[0][0] + result[2][0]
    else:
        q = 0

    print "\n\n\n"
    for r in (result[1] if len(result) == 3 else result[0]):
        print "\n----"
        print (q + r).series(symbolic_functions.e == 0, 0)
        print (q + r).series(symbolic_functions.e == 0, 0).subs(symbolic_functions.p == 1).evalf().expand().evalf().normal().expand()


def main():
    configure.Configure() \
        .with_k_operation(common.MSKOperation()) \
        .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_dimension(const.DIM_PHI4) \
        .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4)) \
        .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()

    operator = r.ROperation()
    g = graph_util.graph_from_str("e111|e|", do_init_weight=True)
    kr_star_quadratic_divergence(operator, g)

    StoragesHolder.instance().close()
    configure.Configure.clear()

if __name__ == "__main__":
    main()


