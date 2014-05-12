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

r.ROperation.set_debug(True)


def kr_star(r_operator, graph):
    _all = [x for x in momentum.xArbitrarilyPassMomentum(graph)]
    # _all = [graph]#[x for x in graphine.momentum.xArbitrarilyPassMomentum(graph)]
    _all.sort(key=common.graph_can_be_calculated_over_n_loops)
    r_star_values = list()
    r_star_graphs = list()
    r_star_op = list()
    for _g in _all:
        # if "e1112|e3|3||:(0, 0)_(1, 0)_(1, 0)_(1, 0)_(1, 0)|(0, 0)_(1, 0)|(1, 0)||::" != str(_g):
        #     continue
        try:
            print "PERFORM", _g
            if common.graph_has_not_ir_divergence(_g):
                r_star_values.append(r_operator.kr1(_g))
                r_star_op.append("KR1")
            else:
                r_star_values.append(r_operator.kr_star(_g))
                r_star_op.append("KR*")
            r_star_graphs.append(_g)
        except common.CannotBeCalculatedError:
            pass
    print "Graph:", graph
    print "R_stars:\n"
    for v, g, o in zip(r_star_values, r_star_graphs, r_star_op):
        print "\t", v
        print "\t", v.subs(symbolic_functions.p == 1).evalf().expand().evalf().normal().expand()
        print "\t for", g
        print "\t used", o
        print "\n"


def main():
    configure.Configure() \
        .with_k_operation(common.MSKOperation()) \
        .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4)) \
        .with_dimension(const.DIM_PHI4) \
        .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4),
                          numerators_util.create_calculator(2, 3, 4)) \
        .with_storage_holder(StorageSettings("phi4", "test", "test").on_shutdown(revert=True)).configure()

    operator = r.ROperation()

    g = graph_util.graph_from_str("ee12|e22|e|", do_init_weight=True, do_init_arrow=True, arrow_lines=[(4, 1), (6, 4)])
    # g = graph_util.graph_from_str("ee12|ee3|344|55|55||", do_init_weight=True)
    kr_star(operator, g)

    StoragesHolder.instance().close()
    configure.Configure.clear()

if __name__ == "__main__":
    main()