#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import graph_state
import common
import const
import inject
import swiginac
from rggraphenv import storage, graph_calculator, symbolic_functions
from rggraphutil import VariableAwareNumber

DEBUG = False
new_edge = graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge


class LazyVal(object):

    def __init__(self, underlying):
        self.undelying = underlying

    def __mul__(self, other):
        if isinstance(other, (swiginac.refcounted, int, float)):
            other = LazyVal(other)
        if isinstance(other, LazyVal):
            return LazyProd((self, other))
        if isinstance(other, LazyProd):
            return LazyProd((self, ) + other.values)
        raise AssertionError()

    __rmul__ = __mul__

    def get(self):
        return self.undelying


class LazyProd(object):
    def __init__(self, values):
        self.values = values

    def get(self):
        return reduce(lambda a, b: a * b.get(), self.values,  swiginac.numeric("1"))

    def __mul__(self, other):
        if isinstance(other, (swiginac.refcounted, int, float)):
            other = LazyVal(other)
        if isinstance(other, LazyVal):
            return LazyProd(self.values + (other, ))
        if isinstance(other, LazyProd):
            return LazyProd(self.values + other.values)
        raise AssertionError()

    __rmul__ = __mul__

UNIT = LazyVal(swiginac.numeric("1"))
ZERO = LazyVal(swiginac.numeric("0"))


def calculate_graphs_values(graphs, suppressException=False):
    return reduce(lambda e, g: e * calculate_graph_value(g, suppressException)[0], graphs, 1)


def calculate_graph_value(graph, suppressException=False):
    if len(graph.edges(graph.external_vertex)) == 2:
        graph_reducer = GGraphReducer(graph)
    else:
        graph_reducer = None
        for g in graphine.momentum.xPassExternalMomentum(graph, common.graph_has_not_ir_divergence_filter):
            graph_reducer = GGraphReducer(g)
            break
        if graph_reducer is None:
            raise common.CannotBeCalculatedError(graph)
    result = graph_reducer.calculate()
    if not result:
        if suppressException:
            return None
        else:
            raise common.CannotBeCalculatedError(graph, "graph can't be calculated")
    if DEBUG:
        print "V(%s)=(%s)*p(-2(%s))" % (graph, common.MSKOperation().calculate(result[0]), result[1])
        print "V(%s)=%s" % (graph, common.MSKOperation().calculate(result[0] * symbolic_functions.p ** (-symbolic_functions.CLN_TWO * result[1].subs(get_lambda()))))
    return result[0] * symbolic_functions.p ** (-symbolic_functions.CLN_TWO * result[1].subs(get_lambda())), graph_reducer.iteration_graphs[0]


def get_lambda():
    return inject.instance("dimension") / swiginac.numeric("2") - swiginac.numeric("1")


def create_filter():
    class RelevanceCondition(object):
        # noinspection PyUnusedLocal
        def isRelevant(self, edgesList, superGraph, superGraphEdges):
            subGraph = graphine.Representator.asGraph(edgesList, superGraph.external_vertex)
            vertexes = set()
            for e in subGraph.edges(superGraph.external_vertex):
                vertexes |= set(e.nodes)
                # external node and 2 internals
            return len(vertexes) == 3
    return graphine.filters.oneIrreducible + graphine.filters.isRelevant(RelevanceCondition())


class GGraphReducer(object):
    START_ID = 666
    END_ID = 777
    DEBUG = False

    FILTER = create_filter()

    @staticmethod
    def set_debug(debug):
        GGraphReducer.DEBUG = debug

    def __init__(self,
                 graph,
                 sub_graph_filters=list(),
                 raw_filters=False,
                 iteration_graphs=None,
                 iteration_values=None,
                 used_arrows=list()):
        """
        momentumPassing -- two external edges of graph in which external momentum passing
        """
        if isinstance(graph, graphine.Graph):
            self._init_graph = graph
        else:
            raise TypeError('unsupported type of initial graph %s' % type(graph))
        graph_str = str(graph)
        self._arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
        self._iteration_graphs = [self._init_graph] if iteration_graphs is None else iteration_graphs
        self._iteration_values = list() if iteration_values is None else iteration_values
        self._sub_graph_filter = sub_graph_filters if raw_filters else (GGraphReducer.FILTER + sub_graph_filters)
        self._is_tadpole = None
        self._used_arrows = used_arrows

    @property
    def iteration_values(self):
        return self._iteration_values

    @property
    def iteration_graphs(self):
        return self._iteration_graphs

    @property
    def external_vertex(self):
        return self._init_graph.external_vertex

    @property
    def iterations_count(self):
        return len(self._iteration_values)

    def get_current_iteration_graph(self):
        return self._iteration_graphs[-1]

    def get_current_iteration_value(self):
        return self._iteration_values[-1] if len(self._iteration_values) else None

    def is_succesful_done(self):
        return len(self.get_current_iteration_graph().allEdges()) == 3 and ("<" not in str(self.get_current_iteration_graph()) and ">" not in str(self.get_current_iteration_graph()))

    def calculate(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        last_iteration = self.get_current_iteration_graph()
        if self._is_tadpole is None:
            self._is_tadpole = str(last_iteration).startswith("ee")
            if self._is_tadpole:
                return ZERO, const.ZERO_WEIGHT

        if (len(last_iteration.allEdges()) == 3 and ("<" not in str(self.get_current_iteration_graph()) and ">" not in str(self.get_current_iteration_graph()))) or str(last_iteration).startswith("ee"):
            if DEBUG:
                print "CALCULATED_GRAPH", self._init_graph, self.iteration_graphs, self.iteration_values
            return self._put_final_value_to_graph_storage()

        res_red = self._try_reduce_chain()
        if res_red is not None:
            return res_red

        relevant_sub_graphs = [x for x in
                               last_iteration.xRelevantSubGraphs(self._sub_graph_filter,
                                                                graphine.Representator.asList)] + \
                              [last_iteration.allEdges()]
        relevant_sub_graphs = relevant_sub_graphs[::-1]
        relevant_sub_graphs.sort(lambda y, x: - len(y) + len(x))

        cached_preprocessed_subgraphs = list()
        for sub_graph_as_list in relevant_sub_graphs:
            adjusted_sub_graph = GGraphReducer._adjust(sub_graph_as_list, self._init_graph.external_vertex)
            subGraph = graphine.Graph(adjusted_sub_graph[0],
                                      external_vertex=self._init_graph.external_vertex)
            preprocessed = (adjusted_sub_graph[1], subGraph, adjusted_sub_graph[2])
            v = inject.instance(storage.StoragesHolder).get_graph(subGraph, 'value')
            if v:
                res = self._do_iterate(preprocessed, v)
                if res is not None:
                    return res
            else:
                cached_preprocessed_subgraphs.append(preprocessed)
                # if DEBUG:
                #     print "has not", subGraph, last_iteration

        cached_preprocessed_subgraphs.reverse()
        for preprocessed in cached_preprocessed_subgraphs:
            if self._arrows_aware:
                _as = filter(lambda e: not e.arrow.is_null(), preprocessed[1].allEdges())
                if len(_as) % 2 == 0:
                    can_calculate = len(self._used_arrows) == 0
                else:
                    assert len(_as) == 1
                    can_calculate = True
            else:
                can_calculate = True
            if can_calculate:
                result = inject.instance(graph_calculator.GraphCalculatorManager).try_calculate(preprocessed[1], put_value_to_storage=True)
                if result is not None:
                    res = self._do_iterate(preprocessed, result[0])
                    if res is not None:
                        return res
                else:
                    if DEBUG:
                        pass
                        # print "cant through calculator1", preprocessed[1], preprocessed[1].getLoopsCount(), last_iteration
            else:
                if DEBUG:
                    pass
                    # print "cant through calculator2", preprocessed[1], preprocessed[1].getLoopsCount(), last_iteration

    def _do_iterate(self, sub_graph_info, iter_sub_graph_value):
        assert len(sub_graph_info[2]) == 2, sub_graph_info[2]
        new_iteration = self.get_current_iteration_graph()
        # iter_sub_graph_value = inject.instance(storage.StoragesHolder).get_graph(sub_graph_info[1], "value")

        new_used_arrows = copy.copy(self._used_arrows)
        for a in self._used_arrows:
            if a in sub_graph_info[0]:
                new_used_arrows.remove(a)
        if self._arrows_aware:
            _as = filter(lambda e: not e.arrow.is_null(), sub_graph_info[1].allEdges())
            if len(_as) % 2 == 0:
                arrow = graph_state.Arrow(graph_state.Arrow.NULL)
            else:
                arrow_direction = 1
                if sub_graph_info[1].allEdges(nickel_ordering=True)[0].marker == GGraphReducer.START_ID:
                    arrow_direction *= -1
                if sub_graph_info[2][0] < sub_graph_info[2][1]:
                    arrow_direction *= -1
                arrow = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW) if arrow_direction == 1 else graph_state.Arrow(graph_state.Arrow.RIGHT_ARROW)
        else:
            arrow = None

        edge = new_edge(sub_graph_info[2],
                        self._init_graph.external_vertex,
                        weight=iter_sub_graph_value[1],
                        arrow=arrow,
                        const=const.MARKER_0 if arrow is None else const.MARKER_1)

        if edge.arrow is not None and not edge.arrow.is_null():
            new_used_arrows.append(edge)

        new_iteration = new_iteration.change(sub_graph_info[0], [edge])

        new_iteration_graphs = copy.copy(self._iteration_graphs)
        new_iteration_graphs.append(new_iteration)
        new_iteration_values = copy.copy(self._iteration_values)
        new_iteration_values.append(iter_sub_graph_value[0])

        new_reducer = GGraphReducer(self._init_graph,
                                    raw_filters=True,
                                    sub_graph_filters=self._sub_graph_filter,
                                    iteration_graphs=new_iteration_graphs,
                                    iteration_values=new_iteration_values,
                                    used_arrows=new_used_arrows)

        return new_reducer.calculate()

    def _try_reduce_chain(self):
        edges_and_vertex = self._search_for_chains()
        if not edges_and_vertex:
            return None
        else:
            edges, v = edges_and_vertex
            assert len(edges) == 2
            if self._arrows_aware:
                edges = list(reversed(edges)) if edges[0].arrow is not None and edges[0].arrow.is_null() else edges
            boundary_vertexes = []
            new_lambda_number = None
            for e in edges:
                if not new_lambda_number:
                    new_lambda_number = e.weight
                else:
                    new_lambda_number += e.weight
                for currentVertex in e.nodes:
                    if currentVertex != v:
                        boundary_vertexes.append(currentVertex)
            assert new_lambda_number
            new_iteration_values = copy.copy(self._iteration_values)
            if self._arrows_aware:
                arrow = graph_state.Arrow(graph_state.Arrow.NULL)
                propagator_arrow_diff_sign = 0
                if not edges[0].arrow.is_null():
                    if edges[1].arrow.is_null():
                        if boundary_vertexes[0] == edges[0].nodes[0]:
                            arrow = edges[0].arrow
                        else:
                            arrow = - edges[0].arrow
                    else:
                        ar0, ar1 = map(lambda e: e.arrow if v == e.nodes[0] else -e.arrow, edges)
                        propagator_arrow_diff_sign = 1 if ar1 != ar0 else -1
                else:
                    assert edges[1].arrow.is_null()
                if propagator_arrow_diff_sign:
                    new_lambda_number -= 1
                    new_iteration_values.append(propagator_arrow_diff_sign)
                newEdge = new_edge(boundary_vertexes,
                                   external_node=self._init_graph.external_vertex,
                                   weight=new_lambda_number,
                                   arrow=arrow,
                                   marker=const.MARKER_1)
            else:
                newEdge = new_edge(boundary_vertexes,
                                   external_node=self._init_graph.external_vertex,
                                   weight=new_lambda_number)
            newIterationGraphs = self._iteration_graphs + [self.get_current_iteration_graph().change(edges, [newEdge])]

            newReducer = GGraphReducer(self._init_graph,
                                       raw_filters=True,
                                       sub_graph_filters=self._sub_graph_filter,
                                       iteration_graphs=newIterationGraphs,
                                       iteration_values=new_iteration_values)

            return newReducer.calculate()

    def _search_for_chains(self):
        current_graph = self.get_current_iteration_graph()
        for v in current_graph.vertices():
            if v is not current_graph.external_vertex:
                edges = current_graph.edges(v)
                if len(edges) == 2:
                    #checks no external edge
                    if current_graph.external_vertex in edges[0].nodes or current_graph.external_vertex in edges[1].nodes:
                        continue
                    return copy.copy(edges), v
        return None

    def get_final_value(self):
        assert self.is_succesful_done()
        if str(self.get_current_iteration_graph()).startswith("ee"):
            return symbolic_functions.CLN_ZERO, const.ZERO_WEIGHT
        g_value = reduce(lambda x, v: x * v, self._iteration_values, UNIT)
        inner_edge = None
        for e in self._iteration_graphs[-1].allEdges():
            if self._init_graph.external_vertex not in e.nodes:
                inner_edge = e
                break
        assert inner_edge

        if DEBUG:
            print "final", self._iteration_graphs
        return g_value, inner_edge.weight

    def _put_final_value_to_graph_storage(self):
        raw_v = self.get_final_value()
        v = raw_v[0].get(), raw_v[1]
        inject.instance(storage.StoragesHolder).put_graph(self._init_graph, v, "value")
        return v

    @staticmethod
    def _adjust(graphAsList, external_vertex):
        adjustedEdges = []
        boundaryVertexes = list()
        boundaryEdges = list()
        adjustedExternalEdges = []
        has_arrows = False
        for e in graphAsList:
            if e.arrow is not None and not e.arrow.is_null():
                has_arrows = not has_arrows
            if external_vertex in e.nodes:
                if e.internal_nodes[0] not in boundaryVertexes:
                    boundaryVertexes.append(e.internal_nodes[0])
                    boundaryEdges.append(e)

            else:
                adjustedEdges.append(e)
        assert len(boundaryEdges) == 2
        boundaryEdges = boundaryEdges if boundaryEdges[0].internal_nodes[0] < boundaryEdges[1].internal_nodes[0] else reversed(boundaryEdges)
        for e, _id in zip(boundaryEdges, (GGraphReducer.START_ID, GGraphReducer.END_ID)):
            adjustedExternalEdges.append(e.copy(marker=_id if has_arrows else None,
                                                arrow=graph_state.Arrow(graph_state.Arrow.NULL) if has_arrows else None))
        return adjustedEdges + adjustedExternalEdges, adjustedEdges, (tuple(boundaryVertexes))
