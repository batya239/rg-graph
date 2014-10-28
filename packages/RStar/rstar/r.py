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
import const
import inject

from rggraphutil import emptyListDict
from rggraphenv import symbolic_functions, log


ValueAndPower = collections.namedtuple("ValueAndPPower", ["value", "p_power"])


@graphine.filters.graph_filter
def is_1uniting(edges_list, super_graph):
    sg_external_edges = graph_state.operations_lib.edges_for_node(edges_list, graph_state.operations_lib.get_external_node(edges_list))
    if len(sg_external_edges) == 2:
        return True

    if len(sg_external_edges) != 1:
        return False
    if ir_uv.uv_index(graphine.Graph(edges_list)) != 2:
        return False


    sg_vertices = graph_state.operations_lib.get_vertices(edges_list)

    bound_vertices = graph_state.operations_lib.get_bound_vertices(sg_external_edges)
    assert len(bound_vertices) == 1

    super_vertices = super_graph.get_bound_vertices() - bound_vertices
    assert len(super_vertices) == 1

    additional_vertex = list(super_vertices)[0]
    for e in super_graph.edges(additional_vertex):
        if not e.is_external():
            c_node = e.co_node(additional_vertex)
            if c_node in sg_vertices:
                return True

    return False



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
        self._k_operation = configure.Configure.k_operation()
        self.storage = configure.Configure.storage()
        self.vertex = 4 if inject.instance("dimension").subs(symbolic_functions.e == 0).to_int() == 4 else 3

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
                    if shrunk.internal_edges_count == 1:
                        continue
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
        _graph = graphine.Graph(map(lambda e: e.copy(marker=None), _graph))
        uv_index = ir_uv.uv_index(_graph)
        do_diff = uv_index == 2
        if do_diff:
            assert not minus_graph
            # return self.kr_star_p2(_graph)
        storage_label = "kr_star_red" if minus_graph else "kr_star"
        evaluated = self.storage.get(_graph.to_tadpole(), storage_label)
        if evaluated is not None:
            return lazy.LazyValue.create(evaluated)
        if uv_index < 0:
            return lazy.ZERO
        iterator = (_graph, ) if minus_graph else momentum.arbitrarily_pass_momentum(_graph, pseudo=do_diff)
        if do_diff and iterator is None:
            return lazy.ZERO
        result = None

        for graph in iterator:
            # if (graph.loops_count == 4 and not str(graph).startswith('e112|33|33|e|:')):
            #     continue
            try:
                if log.is_debug_enabled():
                    debug_line = "KR*(%s)=R~(%s)" % (_graph, graph)
                value = self.renormalize_ir(graph, minus_graph=minus_graph, do_diff=do_diff)
                if value.evaluate().is_zero():
                    return lazy.ZERO
                for counter_item, shrunk, p2_counts, _debug_line in self.x_r_prime(graph):
                    # if p2_counts != 0 and RStar.is_tadpole(shrunk):
                    #     raise common.CannotBeCalculatedError(graph)
                    if do_diff and ir_uv.uv_index(shrunk) == 2 and RStar.is_tadpole(self.adjust(shrunk)):
                        continue
                    if log.is_debug_enabled():
                        debug_line += "+%s*R~(%s)" % (_debug_line, shrunk)
                    value += self.renormalize_ir(shrunk, do_diff=do_diff) * counter_item
                current_result = lazy.LazyValue.create(self._k_operation.calculate(value.evaluate()))
                if log.is_debug_enabled():
                    log.debug(debug_line)
                    log.debug("KR*(%s)=" % _graph + RStar.present_expression(current_result))
                if all_possible:
                    if result is None:
                        result = current_result
                    else:
                        if not result.evaluate().is_equal(current_result.evaluate()):
                            log.debug("WRONG graph = %s,\nvalue1 = %s,\nvalue2 = %s" % (graph, result.evaluate(), current_result.evaluate()))
                else:
                    self.storage.put(_graph.to_tadpole(), current_result, storage_label)
                    return current_result
            except common.CannotBeCalculatedError:
                pass
        if all_possible and result is not None:
            return result
        raise common.CannotBeCalculatedError(_graph)

    def delta_uv(self, _graph):
        value = - self.kr_star(_graph)
        value = value.evaluate()
        value = value.expand()
        if "Order(1)" in str(value):
            value = symbolic_functions.series(value, symbolic_functions.e, 0, 0, remove_order=True)
        return value

    def _delta_ir(self, _graph):
        evaluated = self.storage.get(_graph.to_tadpole(), "delta_ir")
        if evaluated is not None:
            return evaluated
        has_passings = False
        for graph in momentum.arbitrarily_pass_momentum(_graph):
            has_passings = True
            try:
                if log.is_debug_enabled():
                    debug_line = "D_IR(%s)=KR*(%s)" % (_graph, graph)
                if graph.loops_count == 1:
                    return lazy.LazyValue(symbolic_functions.series(RStar.calculate_graph(graph).evaluate(), symbolic_functions.e, 0, 0, True))
                delta_ir = lazy.LazyValue(symbolic_functions.series(self.kr_star(graph.to_tadpole()).evaluate(), symbolic_functions.e, 0, 0, True))
                for counter_item, shrunk, _, debug_line_piece in self.x_r_prime(graph):
                    if self.debug():
                        debug_line += "-" + debug_line_piece + "*D_IR(%s)" % shrunk
                    delta_ir -= counter_item * self._delta_ir(shrunk)
                if log.is_debug_enabled():
                    log.debug(debug_line)
                    log.debug("D_IR(%s)=%s" % (_graph, RStar.present_expression(delta_ir)))
                result = lazy.LazyValue(symbolic_functions.series(delta_ir.evaluate(), symbolic_functions.e, 0, 0, True))
                self.storage.put(_graph.to_tadpole(), result, "delta_ir")
                return result
            except common.CannotBeCalculatedError:
                pass
        if not has_passings:
            return lazy.ZERO
        raise common.CannotBeCalculatedError(_graph)

    def delta_ir(self, _graph):
        return self._delta_ir(_graph).evaluate()

    def renormalize_ir(self, graph, minus_graph=False, do_diff=False):
        storage_label = "r_tilda_red" if minus_graph else "r_tilda"

        evaluated = self.storage.get(graph, storage_label)
        if evaluated is not None:
            return lazy.LazyValue.create(evaluated)
        if RStar.is_tadpole(graph):
            assert not minus_graph
            if str(graph).startswith("ee0"):
                return lazy.ZERO
            if ir_uv.uv_index(graph) == 2 and RStar.is_tadpole(self.adjust(graph)):
                return lazy.ZERO
            return lazy.LazyValue.create(self._delta_ir(graph))
        else:
            if log.is_debug_enabled():
                debug_line = "R~(%s)=V(%s)" % (graph, graph)
            renormalized_g = lazy.ZERO if minus_graph else RStar.calculate_graph(graph, do_diff=do_diff, zero_if_cant=True)
            for co_ir in graph.x_relevant_sub_graphs(graphine.filters.one_irreducible + self._uv_filter + is_1uniting + no_hanging_parts,
                                                     cut_edges_to_external=False,
                                                     result_representator=graphine.Representator.asGraph):
                if ir_uv.uv_index(co_ir) > 0:
                    #TODO implement dalembertian
                    raise common.CannotBeCalculatedError(graph)
                shrunk = graph_util.shrink_to_point(graph, (co_ir, ))[0]
                if shrunk.internal_edges_count == 1:
                    continue
                if log.is_debug_enabled():
                    debug_line += "+V(%s)*D_IR(%s)" % (co_ir, shrunk)
                if str(shrunk).startswith("ee0"):
                    continue
                if do_diff and ir_uv.uv_index(shrunk) == 2 and RStar.is_tadpole(self.adjust(shrunk)):
                    continue
                if do_diff and RStar.is_tadpole(co_ir):
                    continue
                renormalized_g += RStar.calculate_graph(co_ir) * self._delta_ir(shrunk)
            if log.is_debug_enabled():
                log.debug(debug_line)
                log.debug("R~(%s)=%s" % (graph, RStar.present_expression(renormalized_g)))
            self.storage.put(graph, renormalized_g, storage_label)
            return renormalized_g

    def adjust(self, graph):
        to_add = list()
        graph -= graph.external_edges
        for v in graph.vertices:
            to_add_count = self.vertex - reduce(lambda s, e: s + (1 if len(set(e.nodes)) == 2 else 2), graph.edges(v), 0)
            assert to_add_count >= 0, to_add_count
            for i in xrange(to_add_count):
                to_add.append(graph_util.new_edge((graph.external_vertex, v), weight=const.ZERO_WEIGHT))
        return graph + to_add

    @staticmethod
    def calculate_graph(graph, do_diff=False, zero_if_cant=False):
        if RStar.is_tadpole(graph):
            return lazy.ZERO
        if do_diff:
            value = RStar.diff_and_calculate(graph, zero_if_cant=zero_if_cant)
            log.debug("V(%s)=%s" % (graph, RStar.present_expression(value)))
            return value
        value = lazy.LazyValue.create(gfun_calculator.calculate_graph_value(graph))
        log.debug("V(%s)=%s" % (graph, RStar.present_expression(value)))
        return value

    @staticmethod
    def diff_and_calculate(graph, zero_if_cant=False):
        d = diff_util.diff_p2_by_markers(graph)
        if d is None:
            return lazy.ZERO if zero_if_cant else RStar.calculate_graph(graph, do_diff=False)
        value = lazy.ZERO
        for c, g in d:
            value += c * RStar.calculate_graph(g, do_diff=False)
        return value * symbolic_functions.p2

    @staticmethod
    def is_tadpole(graph):
        external_edges = graph.external_edges
        assert len(external_edges) == 2, graph
        if external_edges[0].internal_node == external_edges[1].internal_node:
            return True
        for e in graph.internal_edges:
            if len(set(e.nodes)) == 1:
                return True
        return False

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
        return str(expression.evaluate().series(symbolic_functions.e == 0, 1).expand())

    @staticmethod
    def make_right_2_tails(graph):
        internal_edges = graph.internal_edges
        external_edges_map = dict()
        for e in graph.external_edges:
            external_edges_map[e.internal_node] = e
        return graphine.Graph(internal_edges + tuple(external_edges_map.values()))