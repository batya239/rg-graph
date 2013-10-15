#!/usr/bin/python
# -*- coding: utf8
import itertools
import graphine.filters
import common
import const
import diff_util
import ir_uv

__author__ = 'daddy-bear'

import symbolic_functions
import gfun_calculator
#noinspection PyPep8Naming
import rggraphenv.storage as storage
#noinspection PyPep8Naming
import rggraphutil
import swiginac

DEBUG = False


#noinspection PyUnusedLocal
@graphine.filters.graphFilter
def _is_1uniting(edges_list, super_graph, super_graph_edges):
    sg = graphine.Representator.asGraph(edges_list, super_graph.externalVertex)
    return len(sg.edges(sg.externalVertex)) == 2


#noinspection PyPep8Naming
def KRStar_quadratic_divergence(initial_graph, k_operation, uv_sub_graph_filter,
                                description="", use_graph_calculator=True):
    diff = diff_util.diff_p2(initial_graph)
    result = 0
    for c, g in diff:
        r_star = None
        preferable, not_preferable = \
            graphine.momentum.arbitrarilyPassMomentumWithPreferable(g, common.defaultGraphHasNotIRDivergence)
        for _g in preferable:
            try:
                r_star = KR1(_g, k_operation, uv_sub_graph_filter, description, use_graph_calculator)
                break
            except common.CannotBeCalculatedError:
                pass
        if r_star is None:
            for _g in not_preferable:
                try:
                    r_star = KRStar(_g, k_operation, uv_sub_graph_filter, description, use_graph_calculator)
                    break
                except common.CannotBeCalculatedError:
                    pass
        if r_star is None:
            raise common.CannotBeCalculatedError(g)
        result += k_operation.calculate(c * r_star)
    return result


#noinspection PyPep8Naming
def KRStar(initial_graph, k_operation, uv_sub_graph_filter, description="", use_graph_calculator=True, force=False):
    if len(initial_graph.edges(initial_graph.externalVertex)) == 2:
        iterator = initial_graph,
    else:
        iterator = graphine.Graph.batchInitEdgesColors(graphine.momentum.xArbitrarilyPassMomentum(initial_graph))
    for graph in iterator:
        try:
            # evaluated = storage.getKR1(graph)
            # if evaluated and len(evaluated):
            #     e = evaluated[0]
            #     return e[0].subs(symbolic_functions.p, 1)
            krs = KR1(graph, k_operation, uv_sub_graph_filter, description, use_graph_calculator,
                      force=True,
                      inside_krstar=True).subs(symbolic_functions.p == 1)
            spinneysGenerators = \
                [x for x in graph.xRelevantSubGraphs(filters=graphine.filters.oneIrreducible
                                                     + uv_sub_graph_filter
                                                     + _is_1uniting
                                                     + graphine.filters.vertexIrreducible,
                                                     cutEdgesToExternal=False)]
            for spinney in spinneysGenerators:
                shrunk, p2Counts = shrink_to_point(graph, (spinney,))
                if str(shrunk).startswith("ee0-::"):
                    continue
                spinneyPart = R(spinney,
                                k_operation,
                                uv_sub_graph_filter,
                                use_graph_calculator=use_graph_calculator,
                                force=True,
                                inside_krstar=True).subs(symbolic_functions.p == 1)
                uv = ir_uv.uvIndex(shrunk)
                if uv < 0:
                    raise common.T0OperationNotDefined(shrunk)
                ir = Delta_IR(shrunk, k_operation, uv_sub_graph_filter, description, use_graph_calculator)
                if DEBUG:
                    print "S", spinney, symbolic_functions.safe_integer_numerators(str(spinneyPart.eval()))
                    print "CS", shrunk, symbolic_functions.safe_integer_numerators(str(ir.eval()))
                sub = k_operation.calculate(spinneyPart * ir)
                krs += sub
            if DEBUG:
                print "R*", graph, symbolic_functions.safe_integer_numerators(str(krs.evalf()))
            return krs
        except common.CannotBeCalculatedError:
            pass
    raise common.CannotBeCalculatedError(initial_graph)


#noinspection PyPep8Naming
def Delta_IR(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True):
    #if str(graph).startswith("ee12-23-33--::"):
    #    return symbolic_functions.evaluate("2/3*e**(-1)-1/2*e**(-2)+1/6*e**(-3)")
    #if common.defaultGraphHasNotIRDivergence(graph):
    #    if DEBUG:
    #        print "DELTA_IR = 0", graph
    #    return 0
    #if str(graph) == "ee112-2--::['(0, 0)', '(0, 0)', '(1, 0)', '(1, 0)', '(1, 0)', '(1, 0)']":
    #    return (swiginac.numeric(1)/2) * (1/symbolic_functions.e + 1/symbolic_functions.e/symbolic_functions.e)

    storage_value = storage.getDeltaIR(graph)
    if storage_value is not None:
        return storage_value
    body = graph.deleteEdges(graph.edges(graph.externalVertex))
    kr1 = None
    preferable, notPreferable = \
        graphine.momentum.arbitrarilyPassMomentumWithPreferable(body, common.defaultGraphHasNotIRDivergence)
    for g in preferable:
        try:
            if common.defaultGraphHasNotIRDivergence(g):
                kr1 = KR1(g,
                          kOperation,
                          uvSubGraphFilter,
                          description=description,
                          use_graph_calculator=useGraphCalculator,
                          check_rstar_if_need=False,
                          force=True,
                          inside_krstar=True)
                if DEBUG:
                    _type = "IR R'"
                break
        except common.CannotBeCalculatedError:
            pass
    if kr1 is None:
        for g in notPreferable:
            try:
                kr1 = KRStar(g,
                             kOperation,
                             uvSubGraphFilter,
                             description=description,
                             use_graph_calculator=useGraphCalculator)
                if DEBUG:
                    _type = "IR R*"
                break
            except common.CannotBeCalculatedError:
                pass
    if kr1 is None:
        if str(graph).startswith("ee0-"):
            return 0
        raise common.CannotBeCalculatedError(graph)
    #noinspection PyUnboundLocalVariable
    ir = (kr1 - _do_ir_subtracting_operation(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator)).subs(
        symbolic_functions.p == 1)
    if DEBUG:
        print _type, ir.simplify_indexed().evalf(), g
    storage.putDeltaIR(graph, ir, common.GFUN_METHOD_NAME_MARKER, description=description)
    return ir


def _do_ir_subtracting_operation(raw_graph, k_operation, uv_subgraph_filter, description="", use_graph_calculator=True):
    return 0
    #if len(raw_graph.edges(raw_graph.externalVertex)) == 2:
    #    iterator = [raw_graph]
    #else:
    #    iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.defaultGraphHasNotIRDivergenceFilter)
    #for graph in iterator:
    #    #uv_subgraphs = graphine.Graph.batchInitEdgesColors(
    #    #    [sg for sg in graph.xRelevantSubGraphs(uv_subgraph_filter +
    #    #                                           graphine.filters.oneIrreducible,
    #    #                                           cutEdgesToExternal=True)])
    #    #sub = 0
    #    #sign = 1
    #    #for i in xrange(1, len(uv_subgraphs) + 1):
    #    #    sign *= -1
    #    #    for comb in itertools.combinations(uv_subgraphs, i):
    #    #        if not graphine.util.has_intersecting_by_vertexes_graphs(comb):
    #    #            doContinue = False
    #    #            for _sg in comb:
    #    #                if len(_sg.getBoundVertexes()) == 1:
    #    #                    doContinue = True
    #    #                    break
    #    #            if doContinue:
    #    #                continue
    #    #            r1 = reduce(lambda e, g: e * KR1(g, k_operation, uv_subgraph_filter,
    #    #                                             description=description,
    #    #                                             use_graph_calculator=use_graph_calculator,
    #    #                                             force=True), comb, 1)
    #    #            if r1 != 0:
    #    #                shrunk, p2_counts = shrink_to_point(graph, comb)
    #    #                ir = Delta_IR(shrunk, k_operation, uv_subgraph_filter, description, use_graph_calculator)
    #    #                sub += sign * r1 * ir * (symbolic_functions.p2 ** -p2_counts)
    #    if DEBUG:
    #        print "DELTA_IR", graph, uv_subgraphs
    #    return sub
    #raise common.CannotBeCalculatedError(raw_graph)


#noinspection PyPep8Naming
def KR1(graph, k_operation, uv_sub_graph_filter, description="", use_graph_calculator=True,
        check_rstar_if_need=False, force=False, inside_krstar=False):
    return _do_kr1(graph, k_operation, uv_sub_graph_filter,
                   description=description,
                   use_graph_calculator=use_graph_calculator,
                   check_rstar_if_need=check_rstar_if_need,
                   force=force,
                   inside_krstar=inside_krstar)[0]


def _do_kr1(raw_graph, k_operation, uv_subgraph_filter, description="", use_graph_calculator=True,
            check_rstar_if_need=False, force=False, inside_krstar=False):
    if len(raw_graph.edges(raw_graph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(raw_graph):
            pass
            #raise AssertionError(str(rawGraph) + " - IR divergence")
        iterator = [raw_graph]
    else:
        iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        evaluated = storage.getKR1(graph)
        if evaluated is not None and len(evaluated):
            for e in evaluated:
                return e[0], graph
        try:
            r1 = _do_r1(graph, k_operation, uv_subgraph_filter, description, use_graph_calculator,
                        force=force,
                        inside_krstar=inside_krstar)
            kr1 = k_operation.calculate(r1[0])
            storage.putGraphKR1(r1[1], kr1, common.GFUN_METHOD_NAME_MARKER, description)
            return kr1, graph
        except common.CannotBeCalculatedError:
            pass

    if check_rstar_if_need:
        preferable, not_preferable = \
            graphine.momentum.arbitrarilyPassMomentumWithPreferable(raw_graph, common.defaultGraphHasNotIRDivergence)
        for g in preferable:
            evaluated = storage.getKR1(g)
            if evaluated is not None and len(evaluated):
                for e in evaluated:
                    return e[0], raw_graph
            try:
                kr1 = KR1(g, k_operation, uv_subgraph_filter,
                          description=description,
                          use_graph_calculator=use_graph_calculator,
                          force=False)
            except common.CannotBeCalculatedError:
                pass
            else:
                storage.putGraphKR1(g, kr1, common.GFUN_METHOD_NAME_MARKER, description)
                return kr1, g
        if not inside_krstar:
            for g in not_preferable:
                if g == raw_graph:
                    continue
                evaluated = storage.getKR1(g)
                if evaluated is not None and len(evaluated):
                    for e in evaluated:
                        return e[0], raw_graph
                try:
                    kr1 = KRStar(g, k_operation, uv_subgraph_filter,
                                 description=description,
                                 use_graph_calculator=use_graph_calculator)
                except common.CannotBeCalculatedError:
                    pass
                else:
                    storage.putGraphKR1(g, kr1, common.GFUN_METHOD_NAME_MARKER, description)
                    return kr1, g
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
            kr1 = _do_kr1(graph,
                          k_operation,
                          uv_subgraph_filter,
                          description,
                          use_graph_calculator,
                          force=True,
                          inside_krstar=inside_krstar)[0]
            r = r1 - kr1
            storage.putGraphR(graph, r, common.GFUN_METHOD_NAME_MARKER, description)
            if DEBUG:
                print "R", graph, r.subs(symbolic_functions.p == 1)\
                    .series(symbolic_functions.e == 0, 4)\
                    .simplify_indexed().evalf()
            return r, graph
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


def _do_r1(raw_graph, k_operation, uv_subgraph_filter, description="", use_graph_calculator=True, force=False, inside_krstar=False):
    if len(raw_graph.edges(raw_graph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(raw_graph):
            pass
            #raise AssertionError(str(rawGraph) + " - IR divergence")
        iterator = raw_graph,
    else:
        iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
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
                expression, two_tails_graph = \
                    gfun_calculator.calculateGraphValue(graph, useGraphCalculator=use_graph_calculator)
                if DEBUG:
                    print "R1 no UV", graph, expression
                storage.putGraphR1(two_tails_graph, expression, common.GFUN_METHOD_NAME_MARKER, description)
                return expression, two_tails_graph

            raw_r1 = gfun_calculator.calculateGraphValue(graph, useGraphCalculator=use_graph_calculator)[0]
            if DEBUG:
                debug = []
                print "value", graph, symbolic_functions.series(raw_r1.subs(symbolic_functions.p == 1), symbolic_functions.e, 0, 0).evalf()
            sign = 1
            c_operation = KRStar if inside_krstar else KR1
            for i in xrange(1, len(uv_subgraphs) + 1):
                sign *= -1
                for comb in itertools.combinations(uv_subgraphs, i):
                    if i == 1 or not graphine.util.has_intersecting_by_vertexes_graphs(comb):
                        r1 = reduce(lambda _e, g: _e * c_operation(g, k_operation, uv_subgraph_filter,
                                                                   use_graph_calculator=use_graph_calculator,
                                                                   force=True), comb, 1)
                        shrunk, p2_counts = shrink_to_point(graph, comb)
                        value = gfun_calculator.calculateGraphValue(shrunk,
                                                                    useGraphCalculator=use_graph_calculator)
                        if DEBUG:
                            debug.append('\tc-operation ' + str(r1) + " " + str(comb) + "\n\tshrink "
                                         + str(shrunk) + "value " + str(value[0]))
                            debug.append("\tsum " + str((r1 * value[0]).subs(symbolic_functions.p == 1).series(symbolic_functions.e == 0, 0).evalf()))
                        raw_r1 += sign * r1 * value[0] * (symbolic_functions.p2 ** (-p2_counts))

            if DEBUG:
                print "R1", graph, "UV", uv_subgraphs
                print "R1", graph, k_operation.calculate(raw_r1).subs(symbolic_functions.p == 1).evalf()
                for d in debug:
                    print d
            storage.putGraphR1(graph, raw_r1, common.GFUN_METHOD_NAME_MARKER, description)
            return raw_r1, graph
        except common.CannotBeCalculatedError:
            pass
    raise common.CannotBeCalculatedError(raw_graph)


def shrink_to_point(graph, sub_graphs):
    to_shrink = list()
    p2_counts = 0
    excluded_edges = set()
    for sg in sub_graphs:
        edge = _has_momentum_quadratic_divergence(sg, graph, excluded_edges)
        if edge is not None:
            to_shrink.append(graphine.Graph([edge], graph.externalVertex, renumbering=False))
            p2_counts += 1
        to_shrink.append(sg)
    shrunk = graph.batchShrinkToPoint(to_shrink)
    return shrunk, p2_counts


def _has_momentum_quadratic_divergence(sub_graph, graph, excluded_edges):
    external_edges = sub_graph.edges(sub_graph.externalVertex)
    if len(external_edges) != 2:
        return None
    n_edges = len(sub_graph.allEdges()) - len(external_edges)
    n_vertexes = len(sub_graph.vertices()) - 1
    n_loop = n_edges - n_vertexes + 1
    subgraph_uv_index = n_edges * (-2) + n_loop * 4
    if subgraph_uv_index != 2:
        return None

    border_vertexes = reduce(lambda x, y: x | y,
                             map(lambda x: set(x.nodes),
                                 sub_graph.edges(sub_graph.externalVertex))) - set([sub_graph.externalVertex])

    for bv in border_vertexes:
        sub_graph_edges = sub_graph.edges(bv)
        graph_edges = graph.edges(bv)
        if len(sub_graph_edges) == len(graph_edges):
            raw_edges = set(graph_edges) - set(sub_graph_edges)
            if raw_edges not in external_edges:
                assert len(raw_edges) == 1
                edge = list(raw_edges)[0]
                excluded_edges.add(edge)
                return edge

    assert False


def is_graph_quadratic_divergence(graph):
    return 2 == const.SPACE_DIM * graph.getLoopsCount() + const.EDGE_WEIGHT * len(graph.internalEdges())