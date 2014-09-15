#!/usr/bin/python
# -*- coding: utf8


__author__ = 'dima'

import momentum
import common
import graphine
import collections
import lazy
import graph_state
import gfun_calculator
import graph_util
import configure
import itertools
import ir_uv
import diff_util

from rggraphutil import emptyListDict
from rggraphenv import symbolic_functions, log


ValueAndPower = collections.namedtuple("ValueAndPPower", ["value", "p_power"])

calculate_graph = lambda g: lazy.LazyValue.create(gfun_calculator.calculate_graph_value_with_vertices(g))


@graphine.filters.graph_filter
def is_1uniting(edges_list, super_graph):
    return len(graph_state.operations_lib.edges_for_node(edges_list, graph_state.operations_lib.get_external_node(edges_list))) == 2


@graphine.filters.graph_filter
def no_hanging_parts(edges_list, super_graph):
    sg = graphine.Representator.asGraph(edges_list)
    bound_vertices = sg.get_bound_vertices()
    for e in sg.edges():
        if e.is_external():
            continue
        es = list(sg.edges())
        es.remove(e)
        connected_components = graph_state.operations_lib.get_connected_components(es, additional_vertices=set(e.nodes))
        for connected_component in connected_components:
            if not len(frozenset(connected_component) & bound_vertices):
                return False
    return True


class RStar(object):
    TRIVIAL_GRAPH = object()
    DEBUG = False

    def __init__(self):
        self._uv_filter = configure.Configure.uv_filter()
        self._ir_filter = configure.Configure.ir_filter()
        self._k_operation = configure.Configure.k_operation()
        self.storage = configure.Configure.storage()

    @classmethod
    def set_debug(cls, debug):
        RStar.DEBUG = debug

    @classmethod
    def debug(cls):
        return RStar.DEBUG

    def x_r_prime(self, graph):
        uv_subgraphs = [x for x in graph.x_relevant_sub_graphs(graphine.filters.one_irreducible + self._uv_filter)]
        for i in xrange(1, len(uv_subgraphs) + 1):
            for comb in itertools.combinations(uv_subgraphs, i):
                if i == 1 or not graphine.util.has_intersecting_by_vertices_graphs(comb):
                    shrunk, p2_counts = graph_util.shrink_to_point(graph, comb)
                    counter_item = lazy.LazyValue.create(symbolic_functions.CLN_MINUS_ONE ** i)
                    counter_item *= symbolic_functions.p2 ** (-p2_counts)
                    for g in comb:
                        counter_item *= symbolic_functions.series(self.kr_star(g).evaluate(), symbolic_functions.e, 0, 0, True)
                    debug_line = "(%s)*KR*(%s)" % (symbolic_functions.CLN_MINUS_ONE ** i, comb) if log.is_debug_enabled() else None
                    yield counter_item, shrunk, p2_counts, debug_line

    def kr_star_p2(self, graph, all_possible=False):
        assert len(graph.get_bound_vertices()) == 2
        assert ir_uv.uv_index(graph) == 2
        graph = RStar.make_right_2_tails(graph)
        result = lazy.ZERO
        for g, c in diff_util.dalembertian(graph):
            result += c * self.kr_star(g, all_possible=all_possible)
        result = lazy.LazyValue.create(self._k_operation.calculate(result.evaluate())) * symbolic_functions.p2
        if log.is_debug_enabled():
            log.debug("KR*(%s)=%s" % (graph, result.evaluate()))
        return result

    def kr_star(self, _graph, minus_graph=False, all_possible=False):
        assert not (minus_graph and all_possible)
        uv_index = ir_uv.uv_index(_graph)
        if uv_index == 2:
            assert not minus_graph
            return self.kr_star_p2(_graph)
        storage_label = "kr_star_red" if minus_graph else "kr_star"
        evaluated = self.storage.get_graph(_graph.to_tadpole(), storage_label)
        if evaluated is not None:
            return lazy.LazyValue.create(evaluated)
        if uv_index < 0:
            return lazy.ZERO
        iterator = (_graph, ) if _graph.external_edges_count == 2 else momentum.arbitrarily_pass_momentum(_graph)
        result = None
        for graph in iterator:
            try:
                if log.is_debug_enabled():
                    debug_line = "KR*(%s)=R~(%s)" % (_graph, graph)
                value = self.renormalize_ir(graph, minus_graph=minus_graph)
                if value.evaluate().is_zero():
                    return lazy.ZERO
                for counter_item, shrunk, p2_counts, _debug_line in self.x_r_prime(graph):
                    # if p2_counts != 0 and RStar.is_tadpole(shrunk):
                    #     raise common.CannotBeCalculatedError(graph)
                    if log.is_debug_enabled():
                        debug_line += "+%s*R~(%s)" % (_debug_line, shrunk)
                    value += self.renormalize_ir(shrunk) * counter_item
                current_result = lazy.LazyValue.create(self._k_operation.calculate(value.evaluate()))
                if log.is_debug_enabled():
                    log.debug(debug_line)
                    log.debug("KR*(%s)=" % _graph + RStar.present_expression(current_result))
                if all_possible:
                    if result is None:
                        result = current_result
                    else:
                        if not result.evaluate().is_equal(current_result.evaluate()):
                            log.debug("WRONG graph = %s,\nvalue1 = %s,\nvalue2 = %s" % (_graph, result.evaluate(), current_result.evaluate()))
                else:
                    self.storage.put_graph(_graph.to_tadpole(), current_result, storage_label)
                    return current_result
            except common.CannotBeCalculatedError:
                pass
        if all_possible and result is not None:
            return result
        raise common.CannotBeCalculatedError(_graph)

    def delta_ir(self, _graph):
        evaluated = self.storage.get_graph(_graph.to_tadpole(), "delta_ir")
        if evaluated is not None:
            return evaluated
        has_passings = False
        for graph in momentum.arbitrarily_pass_momentum(_graph):
            has_passings = True
            try:
                if log.is_debug_enabled():
                    debug_line = "D_IR(%s)=KR*(%s)" % (_graph, graph)
                if graph.loops_count == 1:
                    return lazy.LazyValue(symbolic_functions.series(calculate_graph(graph).evaluate(), symbolic_functions.e, 0, 0, True))
                delta_ir = lazy.ZERO
                delta_ir += symbolic_functions.series(self.kr_star(graph.to_tadpole()).evaluate(), symbolic_functions.e, 0, 0, True)
                for counter_item, shrunk, _, debug_line_piece in self.x_r_prime(graph):
                    if self.debug():
                        debug_line += "-" + debug_line_piece + "*D_IR(%s)" % shrunk
                    delta_ir -= counter_item * self.delta_ir(shrunk)
                if log.is_debug_enabled():
                    log.debug(debug_line)
                    log.debug("D_IR(%s)=%s" % (_graph, RStar.present_expression(delta_ir)))
                result = lazy.LazyValue(symbolic_functions.series(delta_ir.evaluate(), symbolic_functions.e, 0, 0, True))
                self.storage.put_graph(_graph.to_tadpole(), result, "delta_ir")
                return result
            except common.CannotBeCalculatedError:
                pass
        if not has_passings:
            return lazy.ZERO
        raise common.CannotBeCalculatedError(_graph)

    def renormalize_ir(self, graph, minus_graph=False):
        storage_label = "r_tilda_red" if minus_graph else "r_tilda"

        evaluated = self.storage.get_graph(graph, storage_label)
        if evaluated is not None:
            return lazy.LazyValue.create(evaluated)
        if RStar.is_tadpole(graph):
            assert not minus_graph
            return lazy.LazyValue.create(self.delta_ir(graph))
        else:
            if log.is_debug_enabled():
                debug_line = "R~(%s)=V(%s)" % (graph, graph)
            renormalized_g = lazy.ZERO if minus_graph else calculate_graph(graph)
            for co_ir in graph.x_relevant_sub_graphs(self._uv_filter + is_1uniting + no_hanging_parts,
                                                     cut_edges_to_external=False,
                                                     result_representator=graphine.Representator.asGraph):
                if ir_uv.uv_index(co_ir) > 0:
                    #TODO implement dalembertian
                    raise common.CannotBeCalculatedError(graph)
                if log.is_debug_enabled():
                    debug_line += "+V(%s)*D_IR(%s)" % (co_ir, graph_util.shrink_to_point(graph, (co_ir, ))[0])
                renormalized_g += calculate_graph(co_ir) * self.delta_ir(graph_util.shrink_to_point(graph, (co_ir, ))[0])
            if log.is_debug_enabled():
                log.debug(debug_line)
                log.debug("R~(%s)=%s" % (graph, RStar.present_expression(renormalized_g)))
            self.storage.put_graph(graph, renormalized_g, storage_label)
            return renormalized_g

    @staticmethod
    def is_tadpole(graph):
        external_edges = graph.external_edges
        assert len(external_edges) == 2
        return external_edges[0].internal_node == external_edges[1].internal_node

    @staticmethod
    def make_two_tails(g):
        g_edges = g.edges(g.external_vertex)
        if len(g_edges) == 2:
            return g
        es = rggraphutil.emptyListDict()
        for e in g_edges:
            es[e.internal_nodes[0]].append(e)
        to_remove = es.values()
        if len(to_remove) == 1:
            return None
        return g - (to_remove[0][1:] + to_remove[1][1:])

    @staticmethod
    def present_expression(expression):
        return str(configure.Configure.k_operation().calculate(expression.evaluate()).expand())

    @staticmethod
    def make_right_2_tails(graph):
        internal_edges = graph.internal_edges
        external_edges_map = dict()
        for e in graph.external_edges:
            external_edges_map[e.internal_node] = e
        return graphine.Graph(internal_edges + tuple(external_edges_map.values()))