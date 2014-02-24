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
import graph_util
import graph_state
import swiginac
import inject
from rggraphenv import symbolic_functions
from rggraphutil import VariableAwareNumber

__author__ = 'daddy-bear'


#noinspection PyUnusedLocal
@graphine.filters.graphFilter
def _is_1uniting(edges_list, super_graph, super_graph_edges):
    sg = graphine.Representator.asGraph(edges_list, super_graph.external_vertex)
    return len(sg.edges(sg.external_vertex)) == 2


class ROperation(object):
    NEGATIVE_WEIGHT_EDGE = VariableAwareNumber("l", -1, 0)
    DEBUG = False

    @classmethod
    def set_debug(cls, debug):
        ROperation.DEBUG = debug

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
        return _do_r1(graph, force)[0]

    def kr1(self, graph, force=False, inside_krstar=False, minus_graph=False):
        return self._do_kr1(graph, force=force, inside_krstar=inside_krstar, minus_graph=minus_graph)[0]

    def kr_star_quadratic_divergence(self, graph):
        diff = diff_util.diff_p2(graph)
        result = 0
        if ROperation.DEBUG:
            print "diff", diff, "initial", graph
        for c, g in diff:
            _all = [x for x in graphine.momentum.xArbitrarilyPassMomentum(g)]
            _all.sort(key=common.graph_can_be_calculated_over_n_loops)
            r_star = None
            for _g in _all:
                if ROperation.DEBUG:
                    print "try", _g
                try:
                    if common.graph_has_not_ir_divergence(_g):
                        r_star = self.kr1(_g)
                    else:
                        r_star = self.kr_star(_g)
                    break
                except common.CannotBeCalculatedError:
                    pass
            if r_star is None:
                raise common.CannotBeCalculatedError(g)
            if ROperation.DEBUG:
                print "diff2 r1", self.k_operation.calculate(r_star).evalf()
                print "diff r1 ", g, _g, self.k_operation.calculate(c * r_star).evalf()
            result += self.k_operation.calculate(c * r_star)
        return result

    def kr_star(self, initial_graph, force=False, minus_graph=False):
        if len(initial_graph.edges(initial_graph.external_vertex)) == 2:
            iterator = initial_graph,
        else:
            iterator = graph_util.batch_init_edges_weight(graphine.momentum.xArbitrarilyPassMomentum(initial_graph))
        for graph in iterator:
            try:
                if not minus_graph:
                    evaluated = self.storage.get_graph(graph, "kr1")
                    if evaluated and len(evaluated):
                        e = evaluated[0]
                        return e.subs(symbolic_functions.p == 1)
                krs = self.kr1(graph,
                               force=True,
                               inside_krstar=True,
                               minus_graph=minus_graph).subs(symbolic_functions.p == 1)
                spinneys_generators = graph.xRelevantSubGraphs(filters=graphine.filters.oneIrreducible
                                                               + self.uv_filter
                                                               + _is_1uniting
                                                               + graphine.filters.vertexIrreducible,
                                                               cutEdgesToExternal=False,
                                                               resultRepresentator=graphine.Representator.asGraph)
                for spinney in spinneys_generators:
                    shrunk, p2Counts = ROperation.shrink_to_point(graph, (spinney,))
                    if str(shrunk).startswith("ee0|:"):
                        continue
                    # switch by uv index
                    uv = ir_uv.uvIndexTadpole(shrunk)
                    if uv < 0:
                        print "T0 not defined", uv, shrunk, spinney, graph
                        raise common.CannotBeCalculatedError(shrunk)
                    spinneyPart = self.r(spinney,
                                         force=True,
                                         inside_krstar=True).subs(symbolic_functions.p == 1)
                    if isinstance(spinneyPart, swiginac.numeric) and spinneyPart.to_double() == 0:
                        continue
                    ir = forest.delta_ir(spinney, graph, self).subs(symbolic_functions.p == 1)
                    if ROperation.DEBUG:
                        print "SPINNEY", spinney, str(spinneyPart.eval())
                        print "CS", shrunk, str(ir.simplify_indexed().evalf())
                    sub = self.k_operation.calculate(spinneyPart * ir)
                    if ROperation.DEBUG:
                        print "SPINNEY_PART", spinney, sub.simplify_indexed().evalf()
                    krs += sub
                if ROperation.DEBUG:
                    print "R*", graph, str(krs.evalf())
                krs = krs.subs(symbolic_functions.p == 1).normal()
                if not force and not minus_graph:
                    self.storage.put_graph(graph, krs, "kr1")
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
            if not force:
                evaluated = self.storage.get_graph(graph, "kr1")
                if evaluated is not None and len(evaluated):
                    for e in evaluated:
                        return e, graph
            try:
                r1 = self._do_r1(graph, force=force, inside_krstar=inside_krstar, minus_graph=minus_graph)
                kr1 = self.k_operation.calculate(r1[0]).normal()
                if not force:
                    self.storage.put_graph(r1[1], kr1, "kr1")
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
            if not force:
                evaluated = storage.getR(graph)
                if evaluated is not None and len(evaluated):
                    for e in evaluated:
                        return e[0], graph
            try:
                r1 = self._do_r1(graph, force=True, inside_krstar=inside_krstar)[0]
                if inside_krstar:
                    kr1 = self.kr_star(graph)
                else:
                    kr1 = self._do_kr1(graph, force=True, inside_krstar=inside_krstar)[0]
                r = r1 - kr1
                if not force:
                    storage.putGraphR(graph, r, common.GFUN_METHOD_NAME_MARKER, description)
                if ROperation.DEBUG:
                    print "R", graph, r.subs(symbolic_functions.p == 1)\
                        .series(symbolic_functions.e == 0, 4)\
                        .simplify_indexed().evalf()
                return r.normal(), graph
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
            if not force:
                evaluated = self.storage.get_graph(graph, "r1")
                if evaluated is not None:
                    for e in evaluated:
                        return e[0], graph
            try:
                uv_subgraphs = filter(lambda _g: _g is not None, map(lambda g: ROperation._two_tails_no_tadpoles(g),
                                                                     graph.xRelevantSubGraphs(self.uv_filter + common.one_irreducible_and_no_tadpoles)))
                if not len(uv_subgraphs):
                    if minus_graph:
                        return swiginac.numeric(0), None
                    expression, two_tails_graph = \
                        gfun_calculator.calculate_graph_value(graph)
                    if ROperation.DEBUG:
                        print "R1 no UV", graph, expression.series(symbolic_functions.e==0, 0).evalf()
                    if not force:
                        self.storage.put_graph(two_tails_graph, expression, "r1")
                    return expression.normal(), two_tails_graph

                raw_r1 = swiginac.numeric(0) if minus_graph else gfun_calculator.calculate_graph_value(graph)[0]
                if ROperation.DEBUG:
                    debug = []
                    print "R1 value", graph, symbolic_functions.series(raw_r1.subs(symbolic_functions.p == 1), symbolic_functions.e, 0, 0).convert_to_poly(True).evalf()
                sign = 1
                c_operation = self.kr_star if inside_krstar else self.kr1
                for i in xrange(1, len(uv_subgraphs) + 1):
                    sign *= -1
                    for comb in itertools.combinations(uv_subgraphs, i):
                        if i == 1 or not graphine.util.has_intersecting_by_vertexes_graphs(comb):
                            r1 = reduce(lambda _e, g: _e * c_operation(g, force=force), comb, 1)
                            shrunk, p2_counts = ROperation.shrink_to_point(graph, comb)
                            value = gfun_calculator.calculate_graph_value(shrunk)
                            if ROperation.DEBUG:
                                debug.append('\tc-operation ' + str(r1) + " " + str(comb) + "\n\tshrink "
                                             + str(shrunk) + " value " + str(value[0].subs(symbolic_functions.p == 1),))
                                debug.append("\tsum " + str((r1 * value[0]).subs(symbolic_functions.p == 1).series(symbolic_functions.e == 0, 0).evalf()))
                            raw_r1 += sign * r1 * value[0] * (symbolic_functions.p2 ** (-p2_counts))
                if ROperation.DEBUG:
                    print "R1", graph, "UV", uv_subgraphs
                    print "R1", graph, self.k_operation.calculate(raw_r1).subs(symbolic_functions.p == 1).evalf()
                    for d in debug:
                        print d
                if not force:
                    self.storage.put_graph(graph, raw_r1, "r1")
                return raw_r1.normal(), graph
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