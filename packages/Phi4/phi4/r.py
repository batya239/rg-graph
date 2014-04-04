#!/usr/bin/python
# -*- coding: utf8
import itertools
import graphine.filters
import common
import const
import diff_util
import ir_uv
import gfun_calculator
import rggraphenv
import rggraphutil
import forest
import copy
import graph_util
import graph_state
import swiginac
import inject
import graph_pole_part_calculator
from rggraphenv import symbolic_functions
from rggraphutil import VariableAwareNumber
from reduction import reductor

__author__ = 'daddy-bear'


#noinspection PyUnusedLocal
@graphine.filters.graphFilter
def _is_1uniting(edges_list, super_graph, super_graph_edges):
    sg = graphine.Representator.asGraph(edges_list, super_graph.external_vertex)
    return len(sg.edges(sg.external_vertex)) == 2


@graphine.filters.graphFilter
def _no_hanging_parts(edges_list, super_graph, super_graph_edges):
    """
    no hangings parts as tadpoles or single edges
    """
    sg = graphine.Representator.asGraph(edges_list, super_graph.external_vertex)
    bound_vertices = sg.getBoundVertexes()
    for e in sg.allEdges():
        if e.is_external():
            continue
        es = copy.copy(sg.allEdges())
        es.remove(e)
        connected_components = graphine.graph_operations._get_connected_components(es,
                                                                                   sg.external_vertex)
        for connected_component in connected_components:
            if not len(frozenset(connected_component) & bound_vertices):
                return False

    # example eye -- bubble
    # for v in sg.vertices():
    #     if v is sg.external_vertex or v in bound_vertices:
    #         continue
    #     connected_components = graphine.graph_operations._get_connected_components(sg.allEdges(),
    #                                                                                sg.external_vertex,
    #                                                                                singularVertexes=frozenset((v,)))
    #     for connected_component in connected_components:
    #         if not len(frozenset(connected_component) & bound_vertices):
    #             return False

    return True


class ROperation(object):
    NEGATIVE_WEIGHT_EDGE = VariableAwareNumber("l", -1, 0)
    DEBUG = False

    @classmethod
    def set_debug(cls, debug):
        forest.DEBUG = debug
        ROperation.DEBUG = debug
        reductor.DEBUG = debug
        gfun_calculator.DEBUG = debug
        graph_pole_part_calculator.DEBUG = debug

    def __init__(self):
        self.storage = inject.instance(rggraphenv.storage.StoragesHolder)
        self.ir_filter = inject.instance("ir_filter")
        self.uv_filter = inject.instance("uv_filter")
        self.k_operation = inject.instance("k_operation")

    def r(self, graph, force=False, inside_krstar=False):
        return self._do_r(graph,
                          force=force,
                          inside_krstar=inside_krstar)[0]

    def r1(self, graph, force=False):
        return self._do_r1(graph, force)[0]

    def kr1(self, graph, force=False, inside_krstar=False, minus_graph=False):
        return self._do_kr1(graph, force=force, inside_krstar=inside_krstar, minus_graph=minus_graph)[0]

    def kr_star_quadratic_divergence(self, graph):
        diff = diff_util.diff_p2(graph)
        if ROperation.DEBUG:
            debug_line = "KR_STAR(%s)=" % graph.getPresentableStr()
        result = symbolic_functions.CLN_ZERO
        for c, g in diff:
            _all = [x for x in graphine.momentum.xArbitrarilyPassMomentum(g)]
            _all.sort(key=common.graph_can_be_calculated_over_n_loops)
            r_star = None
            for _g in _all:
                try:
                    if common.graph_has_not_ir_divergence(_g):
                        r_star = self.kr1(_g)
                    else:
                        r_star = self.kr_star(_g)
                    result += self.k_operation.calculate(c * r_star)
                    break
                except common.CannotBeCalculatedError:
                    pass
            if r_star is None:
                raise common.CannotBeCalculatedError(g)
            if ROperation.DEBUG:
                debug_line += "+(%s)*KR_STAR(%s)" % (c, _g.getPresentableStr())
        if ROperation.DEBUG:
            print debug_line
        return result

    def kr_star(self, initial_graph, force=False, minus_graph=False):
        if len(initial_graph.edges(initial_graph.external_vertex)) == 2:
            iterator = initial_graph,
        else:
            iterator = [x for x in graph_util.batch_init_edges_weight(graphine.momentum.xArbitrarilyPassMomentum(initial_graph))]
        for graph in iterator:
            try:
                evaluated = self.storage.get_graph((graph, force, minus_graph, "star"), "kr1")
                if evaluated is not None:
                    return evaluated

                spinneys_generators = [x for x in graph.xRelevantSubGraphs(filters=self.uv_filter + _is_1uniting + _no_hanging_parts,
                                                                           cutEdgesToExternal=False,
                                                                           resultRepresentator=graphine.Representator.asGraph)]

                for spinney in spinneys_generators:
                    uv = ir_uv.uvIndex(spinney)
                    if uv > 0:
                        # print "T0 not defined", uv, shrunk, spinney, graph
                        raise common.CannotBeCalculatedError(spinney)
                    if not graphine.graph_operations.isGraph1Irreducible(spinney.allEdges(), graph, None):
                        raise common.CannotBeCalculatedError(spinney)

                if ROperation.DEBUG:
                    debug_line = "KR_Star(%s)=KR1(%s)" % (graph, graph)
                krs = self.kr1(graph,
                               force=True,
                               inside_krstar=True,
                               minus_graph=minus_graph)

                for spinney in spinneys_generators:
                    # switch by uv index
                    # uv = ir_uv.uvIndex(spinney)
                    # if uv > 0:
                    #     # print "T0 not defined", uv, shrunk, spinney, graph
                    #     raise common.CannotBeCalculatedError(spinney)
                    shrunk, p2_counts = ROperation.shrink_to_point(graph, (spinney,))
                    if str(shrunk).startswith("ee0|:"):
                        continue
                    if ROperation.DEBUG:
                        debug_line += "+K(R(%s)*Delta_IR(%s))" % (spinney, shrunk)
                    spinney_part = self.r(spinney,
                                          force=True,
                                          inside_krstar=True)
                    if isinstance(spinney_part, swiginac.numeric) and spinney_part.to_double() == 0:
                        continue
                    ir = forest.delta_ir(spinney, graph, shrunk, self)
                    ir = symbolic_functions.series(ir, symbolic_functions.e, symbolic_functions.CLN_ZERO, 0, True)
                    assert p2_counts == 0
                    sub = self.k_operation.calculate(spinney_part * ir)
                    krs += sub
                krs = self.k_operation.calculate(krs)
                if ROperation.DEBUG:
                    print debug_line
                    print "KR_Star(%s) = %s" % (graph, krs)
                self.storage.put_graph((graph, force, minus_graph, "star"), krs, "kr1")
                return krs
            except common.CannotBeCalculatedError:
                pass
        raise common.CannotBeCalculatedError(initial_graph)

    def _do_kr1(self, raw_graph, force=False, inside_krstar=False, minus_graph=False):
        if len(raw_graph.edges(raw_graph.external_vertex)) == 2:
            if not force and not common.graph_has_not_ir_divergence(raw_graph):
                raise AssertionError(str(raw_graph) + " - IR divergence")
            iterator = raw_graph,
        else:
            iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.graph_has_not_ir_divergence_filter)
        for graph in iterator:
            evaluated = self.storage.get_graph((graph, force, inside_krstar, minus_graph, "1"), "kr1")
            if evaluated is not None:
                return evaluated, graph
            try:
                r1 = self._do_r1(graph, force=force, inside_krstar=inside_krstar, minus_graph=minus_graph)
                kr1 = self.k_operation.calculate(r1[0])
                if ROperation.DEBUG:
                    print "KR1(%s)=%s" % (graph, kr1)
                self.storage.put_graph((r1[1], force, inside_krstar, minus_graph, "1"), kr1, "kr1")
                return kr1, graph
            except common.CannotBeCalculatedError:
                pass
        raise common.CannotBeCalculatedError(raw_graph)

    def _do_r(self, raw_graph, force=False, inside_krstar=False):
        if len(raw_graph.edges(raw_graph.external_vertex)) == 2:
            if not force and not common.graph_has_not_ir_divergence(raw_graph):
                raise AssertionError(str(raw_graph) + " - IR divergence")
            iterator = raw_graph,
        else:
            iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.graph_has_not_ir_divergence_filter)
        for graph in iterator:
            evaluated = self.storage.get_graph((graph, force, inside_krstar), "r")
            if evaluated is not None:
                return evaluated, graph
            try:
                r1 = self._do_r1(graph, force=True, inside_krstar=inside_krstar)[0]
                if inside_krstar:
                    kr1 = self.kr_star(graph)
                else:
                    kr1 = self._do_kr1(graph, force=True, inside_krstar=inside_krstar)[0]
                r = r1 - symbolic_functions.series(kr1, symbolic_functions.e, symbolic_functions.CLN_ZERO, 0, True)
                r = r.expand()
                self.storage.put_graph((graph, force, inside_krstar), r, "r")
                return r, graph
            except common.CannotBeCalculatedError:
                pass
        raise common.CannotBeCalculatedError(raw_graph)

    def _do_r1(self, raw_graph, force=False, inside_krstar=False, minus_graph=False):
        if minus_graph:
            assert force
        if len(raw_graph.edges(raw_graph.external_vertex)) == 2:
            if not force and not common.graph_has_not_ir_divergence(raw_graph):
                raise AssertionError(str(raw_graph) + " - IR divergence")
            iterator = raw_graph,
        else:
            iterator = graphine.momentum.xPassExternalMomentum(raw_graph, common.graph_has_not_ir_divergence_filter)
        for graph in iterator:
            evaluated = self.storage.get_graph((graph, force, inside_krstar, minus_graph), "r1")
            if evaluated is not None:
                return evaluated, graph
            try:
                uv_subgraphs = filter(lambda _g: _g is not None, map(lambda g: ROperation._two_tails_no_tadpoles(g),
                                                                     graph.xRelevantSubGraphs(self.uv_filter + common.one_irreducible_and_no_tadpoles)))
                if not len(uv_subgraphs):
                    if minus_graph:
                        return symbolic_functions.CLN_ZERO, None
                    expression, two_tails_graph = \
                        gfun_calculator.calculate_graph_value(graph)
                    if ROperation.DEBUG:
                        print "R1(%s)=V(%s)" % (graph, graph)
                    self.storage.put_graph((two_tails_graph, force, inside_krstar), expression, "r1")
                    return expression, two_tails_graph

                raw_r1 = symbolic_functions.CLN_ZERO if minus_graph else gfun_calculator.calculate_graph_value(graph)[0]
                if ROperation.DEBUG:
                    debug_line = "R1(%s)=V(%s)" % (graph, graph)
                sign = symbolic_functions.CLN_ONE
                c_operation = self.kr_star if inside_krstar else self.kr1
                for i in xrange(1, len(uv_subgraphs) + 1):
                    sign *= symbolic_functions.CLN_MINUS_ONE
                    for comb in itertools.combinations(uv_subgraphs, i):
                        if i == 1 or not graphine.util.has_intersecting_by_vertexes_graphs(comb):
                            r1 = reduce(lambda _e, g: _e * symbolic_functions.series(c_operation(g, force=force), symbolic_functions.e, symbolic_functions.CLN_ZERO, 0, True), comb, symbolic_functions.CLN_ONE)
                            shrunk, p2_counts = ROperation.shrink_to_point(graph, comb)
                            value = gfun_calculator.calculate_graph_value(shrunk)
                            if ROperation.DEBUG:
                                debug_line += "+(%s)*KR1(%s)*V(%s)" % (sign, comb, shrunk)
                            raw_r1 += sign * r1 * value[0] * (symbolic_functions.p2 ** (-p2_counts))
                if ROperation.DEBUG:
                    print debug_line
                self.storage.put_graph((graph, force, inside_krstar, minus_graph), raw_r1, "r1")
                return raw_r1, graph
            except common.CannotBeCalculatedError:
                pass
        raise common.CannotBeCalculatedError(raw_graph)

    @staticmethod
    def _two_tails_no_tadpoles(g):
        g_edges = g.edges(g.external_vertex)
        if len(g_edges) == 2:
            return g
        es = rggraphutil.emptyListDict()
        for e in g_edges:
            es[e.internal_nodes[0]].append(e)
        to_remove = es.values()
        if len(to_remove) == 1:
            return None
        return g.deleteEdges(to_remove[0][1:] + to_remove[1][1:])

    @staticmethod
    def shrink_to_point(graph, sub_graphs):
        to_shrink = list()
        to_replace_by_edge = list()
        p2_counts = 0
        for sg in sub_graphs:
            edge = ROperation.has_momentum_quadratic_divergence(sg)
            if edge is not None:
                to_replace_by_edge.append((edge, sg))
                graph = graph.change(sg.internalEdges(), (edge,), renumbering=False)
                p2_counts += 1
            else:
                to_shrink.append(sg)
        shrunk = graph.batchShrinkToPoint(to_shrink)

        # for e in shrunk.allEdges():
        #     if e.weight == -1:
        #         do_next = False
        #         for v in e.nodes:
        #             v_edges = shrunk.edges(v)
        #             if len(v_edges) == 2
        #
        return shrunk, p2_counts

    @staticmethod
    def has_momentum_quadratic_divergence(sub_graph):
        if sub_graph.externalEdgesCount() != 2:
            return None

        subgraph_uv_index = ir_uv.uvIndex(sub_graph)
        if subgraph_uv_index != 2:
            return None

        border_vertexes = sub_graph.getBoundVertexes()

        assert len(border_vertexes) == 2

        graph_str = str(sub_graph)
        arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
        arrow = graph_state.Arrow(graph_state.Arrow.NULL) if arrows_aware else None
        return graph_util.new_edge(tuple(border_vertexes), weight=ROperation.NEGATIVE_WEIGHT_EDGE, arrow=arrow)