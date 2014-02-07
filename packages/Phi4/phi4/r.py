#!/usr/bin/python
# -*- coding: utf8
import itertools
import graphine.filters
import common
import const
import diff_util
import ir_uv
import gfun_calculator
import rggraphenv.storage as storage
import rggraphutil
import forest
import graph_util
import graph_state
import swiginac
from rggraphenv import symbolic_functions

__author__ = 'daddy-bear'


DEBUG = False


#noinspection PyUnusedLocal
@graphine.filters.graphFilter
def _is_1uniting(edges_list, super_graph, super_graph_edges):
    sg = graphine.Representator.asGraph(edges_list, super_graph.externalVertex)
    return len(sg.edges(sg.externalVertex)) == 2


#noinspection PyPep8Naming
def KRStar_quadratic_divergence(initial_graph,
                                k_operation,
                                uv_sub_graph_filter,
                                description="",
                                use_graph_calculator=True,
                                do_kr_star=True):
    diff = diff_util.diff_p2(initial_graph)
    result = 0
    if DEBUG:
        print "diff", diff, "initial", initial_graph
    for c, g in diff:
        _all = [x for x in graphine.momentum.xArbitrarilyPassMomentum(g)]
        _all.sort(key=common.graph_can_be_calculated_over_n_loops)
        r_star = None
        for _g in _all:
            if DEBUG:
                print "try", _g
            try:
                if common.defaultGraphHasNotIRDivergence(_g):
                    r_star = KR1(_g, k_operation, uv_sub_graph_filter, description, use_graph_calculator)
                else:
                    r_star = KRStar(_g, k_operation, uv_sub_graph_filter, description, use_graph_calculator)
                break
            except common.CannotBeCalculatedError:
                pass
        if r_star is None:
            raise common.CannotBeCalculatedError(g)
        if DEBUG:
            print "diff2 r1", k_operation.calculate(r_star).evalf()
            print "diff r1 ", g, _g, k_operation.calculate(c * r_star).evalf()
        result += k_operation.calculate(c * r_star)
    return result


#noinspection PyPep8Naming
def KRStar(initial_graph, k_operation, uv_sub_graph_filter, description="", use_graph_calculator=True, force=False, minus_graph=False):
    if len(initial_graph.edges(initial_graph.externalVertex)) == 2:
        iterator = initial_graph,
    else:
        iterator = graph_util.batch_init_edges_colors(graphine.momentum.xArbitrarilyPassMomentum(initial_graph))
    for graph in iterator:
        try:
            if not minus_graph:
                evaluated = storage.getKR1(graph)
                if evaluated and len(evaluated):
                    e = evaluated[0]
                    return e[0].subs(symbolic_functions.p == 1)
            krs = KR1(graph, k_operation, uv_sub_graph_filter, description, use_graph_calculator,
                      force=True,
                      inside_krstar=True,
                      minus_graph=minus_graph).subs(symbolic_functions.p == 1)
            spinneys_generators = graph.xRelevantSubGraphs(filters=graphine.filters.oneIrreducible
                                                           + uv_sub_graph_filter
                                                           + _is_1uniting
                                                           + graphine.filters.vertexIrreducible,
                                                           cutEdgesToExternal=False,
                                                           resultRepresentator=graphine.Representator.asGraph)
            for spinney in spinneys_generators:
                shrunk, p2Counts = shrink_to_point(graph, (spinney,))
                if str(shrunk).startswith("ee0|:"):
                    continue
                # switch by uv index
                uv = ir_uv.uvIndexTadpole(shrunk)
                if uv < 0:
                    print "T0 not defined", uv, shrunk, spinney, graph
                    raise common.CannotBeCalculatedError(shrunk)
                spinneyPart = R(spinney,
                                k_operation,
                                uv_sub_graph_filter,
                                use_graph_calculator=use_graph_calculator,
                                force=True,
                                inside_krstar=True).subs(symbolic_functions.p == 1)
                if isinstance(spinneyPart, swiginac.numeric) and spinneyPart.to_double() == 0:
                    continue
                ir = forest.Delta_IR(spinney, graph, k_operation, uv_sub_graph_filter, description, use_graph_calculator)\
                    .subs(symbolic_functions.p == 1)
                if DEBUG:
                    print "SPINNEY", spinney, str(spinneyPart.eval())
                    print "CS", shrunk, str(ir.simplify_indexed().evalf())
                sub = k_operation.calculate(spinneyPart * ir)
                if DEBUG:
                    print "SPINNEY_PART", spinney, sub.simplify_indexed().evalf()
                krs += sub
            if DEBUG:
                print "R*", graph, str(krs.evalf())
            krs = krs.subs(symbolic_functions.p == 1).normal()
            if not force and not minus_graph:
                storage.putGraphKR1(graph, krs, common.GFUN_METHOD_NAME_MARKER, description)
            return krs
        except common.CannotBeCalculatedError:
            pass
    raise common.CannotBeCalculatedError(initial_graph)


#noinspection PyPep8Naming
def KR1(graph, k_operation, uv_sub_graph_filter, description="", use_graph_calculator=True, force=False, inside_krstar=False, minus_graph=False):
    return _do_kr1(graph, k_operation, uv_sub_graph_filter, description=description, use_graph_calculator=use_graph_calculator,
                   force=force, inside_krstar=inside_krstar, minus_graph=minus_graph)[0]


def _do_kr1(raw_graph, k_operation, uv_subgraph_filter, description="", use_graph_calculator=True, force=False, inside_krstar=False, minus_graph=False):
    if len(raw_graph.edges(raw_graph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(raw_graph):
            raise AssertionError(str(raw_graph) + " - IR divergence")
        iterator = raw_graph,
    else:
        iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        if not force:
            evaluated = storage.getKR1(graph)
            if evaluated is not None and len(evaluated):
                for e in evaluated:
                    return e[0], graph
        try:
            r1 = _do_r1(graph, k_operation, uv_subgraph_filter, description, use_graph_calculator,
                        force=force,
                        inside_krstar=inside_krstar,
                        minus_graph=minus_graph)
            kr1 = k_operation.calculate(r1[0]).normal()
            if not force:
                storage.putGraphKR1(r1[1], kr1, common.GFUN_METHOD_NAME_MARKER, description)
            return kr1, graph
        except common.CannotBeCalculatedError:
            pass
    raise common.CannotBeCalculatedError(raw_graph)


#noinspection PyPep8Naming
def R(graph,
      k_operation,
      uv_subgraph_filter,
      description="",
      use_graph_calculator=True,
      force=False,
      inside_krstar=False):
    """
    R = (1-K)R'
    """
    return _do_r(graph, k_operation, uv_subgraph_filter,
                 description=description,
                 use_graph_calculator=use_graph_calculator,
                 force=force,
                 inside_krstar=inside_krstar)[0]


def _do_r(raw_graph,
          k_operation,
          uv_subgraph_filter,
          description="",
          use_graph_calculator=True,
          force=False,
          inside_krstar=False):
    if len(raw_graph.edges(raw_graph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(raw_graph):
            raise AssertionError(str(raw_graph) + " - IR divergence")
        iterator = raw_graph,
    else:
        iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        if not force:
            evaluated = storage.getR(graph)
            if evaluated is not None and len(evaluated):
                for e in evaluated:
                    return e[0], graph
        try:
            r1 = _do_r1(graph,
                        k_operation,
                        uv_subgraph_filter,
                        description,
                        use_graph_calculator,
                        force=True,
                        inside_krstar=inside_krstar)[0]
            if inside_krstar:
                kr1 = KRStar(graph,
                             k_operation,
                             uv_subgraph_filter,
                             description=description,
                             use_graph_calculator=use_graph_calculator)
            else:
                kr1 = _do_kr1(graph,
                              k_operation,
                              uv_subgraph_filter,
                              description,
                              use_graph_calculator,
                              force=True,
                              inside_krstar=inside_krstar)[0]
            r = r1 - kr1
            if not force:
                storage.putGraphR(graph, r, common.GFUN_METHOD_NAME_MARKER, description)
            if DEBUG:
                print "R", graph, r.subs(symbolic_functions.p == 1)\
                    .series(symbolic_functions.e == 0, 4)\
                    .simplify_indexed().evalf()
            return r.normal(), graph
        except common.CannotBeCalculatedError:
            pass
    raise common.CannotBeCalculatedError(raw_graph)


#noinspection PyPep8Naming
def R1(graph, k_operation, uv_subgraph_filter, description="", use_graph_calculator=True, force=False):
    return _do_r1(graph, k_operation, uv_subgraph_filter, description, use_graph_calculator, force)[0]


def _two_tails_no_tadpoles(g):
    g_edges = g.edges(g.externalVertex)
    if len(g_edges) == 2:
        return g
    es = rggraphutil.emptyListDict()
    for e in g_edges:
        es[e.internal_nodes[0]].append(e)
    to_remove = es.values()
    if len(to_remove) == 1:
        return None
    return g.deleteEdges(to_remove[0][1:] + to_remove[1][1:])


def _do_r1(raw_graph, k_operation, uv_subgraph_filter, description="", use_graph_calculator=True, force=False, inside_krstar=False, minus_graph=False):
    if minus_graph:
        assert force
    if len(raw_graph.edges(raw_graph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(raw_graph):
            raise AssertionError(str(raw_graph) + " - IR divergence")
        iterator = raw_graph,
    else:
        iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        if not force:
            evaluated = storage.getR1(graph)
            if evaluated is not None:
                for e in evaluated:
                    return e[0], graph
        try:
            uv_subgraphs = filter(lambda _g: _g is not None, map(lambda g: _two_tails_no_tadpoles(g),
                                                                 graph.xRelevantSubGraphs(
                                                                     uv_subgraph_filter +
                                                                     common.oneIrreducibleAndNoTadpoles)))
            if not len(uv_subgraphs):
                if minus_graph:
                    return swiginac.numeric(0), None
                expression, two_tails_graph = \
                    gfun_calculator.calculateGraphValue(graph, useGraphCalculator=use_graph_calculator)
                if DEBUG:
                    print "R1 no UV", graph, expression.series(symbolic_functions.e==0, 0).evalf()
                if not force:
                    storage.putGraphR1(two_tails_graph, expression, common.GFUN_METHOD_NAME_MARKER, description)
                return expression.normal(), two_tails_graph

            raw_r1 = swiginac.numeric(0) if minus_graph else gfun_calculator.calculateGraphValue(graph, useGraphCalculator=use_graph_calculator)[0]
            if DEBUG:
                debug = []
                print "R1 value", graph, symbolic_functions.series(raw_r1.subs(symbolic_functions.p == 1), symbolic_functions.e, 0, 0).convert_to_poly(True).evalf()
            sign = 1
            c_operation = KRStar if inside_krstar else KR1
            for i in xrange(1, len(uv_subgraphs) + 1):
                sign *= -1
                for comb in itertools.combinations(uv_subgraphs, i):
                    if i == 1 or not graphine.util.has_intersecting_by_vertexes_graphs(comb):
                        r1 = reduce(lambda _e, g: _e * c_operation(g, k_operation, uv_subgraph_filter,
                                                                   use_graph_calculator=use_graph_calculator,
                                                                   force=force), comb, 1)
                        shrunk, p2_counts = shrink_to_point(graph, comb)
                        value = gfun_calculator.calculateGraphValue(shrunk,
                                                                    useGraphCalculator=use_graph_calculator)
                        if DEBUG:
                            debug.append('\tc-operation ' + str(r1) + " " + str(comb) + "\n\tshrink "
                                         + str(shrunk) + " value " + str(value[0].subs(symbolic_functions.p == 1),))
                            debug.append("\tsum " + str((r1 * value[0]).subs(symbolic_functions.p == 1).series(symbolic_functions.e == 0, 0).evalf()))
                        raw_r1 += sign * r1 * value[0] * (symbolic_functions.p2 ** (-p2_counts))

            if DEBUG:
                print "R1", graph, "UV", uv_subgraphs
                print "R1", graph, k_operation.calculate(raw_r1).subs(symbolic_functions.p == 1).evalf()
                for d in debug:
                    print d
            if not force:
                storage.putGraphR1(graph, raw_r1, common.GFUN_METHOD_NAME_MARKER, description)
            return raw_r1.normal(), graph
        except common.CannotBeCalculatedError:
            pass
    raise common.CannotBeCalculatedError(raw_graph)


def shrink_to_point(graph, sub_graphs):
    to_shrink = list()
    to_replace_by_edge = list()
    p2_counts = 0
    for sg in sub_graphs:
        edge = _has_momentum_quadratic_divergence(sg)
        if edge is not None:
            to_replace_by_edge.append((edge, sg))
            graph = graph.change(sg.internalEdges(), (edge,), renumbering=False)
            p2_counts += 1
        else:
            to_shrink.append(sg)
    shrunk = graph.batchShrinkToPoint(to_shrink)
    return shrunk, p2_counts


NEGATIVE_WEIGHT_EDGE = graph_state.Rainbow((-1, 0))


def _has_momentum_quadratic_divergence(sub_graph):
    if sub_graph.externalEdgesCount() != 2:
        return None

    subgraph_uv_index = ir_uv.uvIndex(sub_graph)
    if subgraph_uv_index != 2:
        return None

    border_vertexes = sub_graph.getBoundVertexes()

    assert len(border_vertexes) == 2
    return graph_util.new_edge(tuple(border_vertexes), colors=NEGATIVE_WEIGHT_EDGE)