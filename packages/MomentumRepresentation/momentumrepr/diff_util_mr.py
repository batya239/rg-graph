#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import itertools
import graphine
import inject
import swiginac
import configure_mr
import graphine
import copy
import graph_util_mr
import graph_state
from rggraphenv import symbolic_functions


def construct_graph_with_markers(graph, minimal_passing):
    new_graph_edges = map(lambda e: e.copy(marker=graph_util_mr.MARKER_0), graph.allEdges())
    new_minimal_passing = list()
    for e, b in minimal_passing:
        new_graph_edges.remove(e.copy(marker=graph_util_mr.MARKER_0))
        new_e = e.copy(marker=graph_util_mr.MARKER_1)
        new_graph_edges.append(new_e)
        new_minimal_passing.append((new_e, b))
    return graphine.Graph(new_graph_edges, external_vertex=graph.external_vertex, renumbering=False), new_minimal_passing


CLN_FOUR = swiginac.numeric("4")


def c1():
    return CLN_FOUR / configure_mr.Configure.dimension()


def c2():
    return CLN_FOUR / configure_mr.Configure.dimension()


def c3():
    return symbolic_functions.CLN_MINUS_ONE


def combinations_with_replacement(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)


if 'combinations_with_replacement' not in itertools.__dict__:
    itertools.combinations_with_replacement = combinations_with_replacement


def _do_diff(graph, comb):
    if comb[0] == comb[1]:
        #
        # (d_xi)^2
        #
        all_edges_3edges = copy.copy(graph.allEdges())
        edge = comb[0][0]
        all_edges_3edges.remove(edge)
        new_vertex1, new_vertex2 = graph.createVertexIndex(), graph.createVertexIndex()
        numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW)
        all_edges_3edges.append(graph_util_mr.new_edge((edge.nodes[0], new_vertex1),
                                                       flow=edge.flow,
                                                       fields=edge.fields,
                                                       arrow=numerator,
                                                       marker=edge.marker,
                                                       external_node=graph.external_vertex))
        all_edges_3edges.append(graph_util_mr.new_edge((new_vertex1, new_vertex2),
                                                       flow=edge.flow,
                                                       fields=edge.fields,
                                                       arrow=numerator,
                                                       marker=edge.marker,
                                                       external_node=graph.external_vertex))
        all_edges_3edges.append(graph_util_mr.new_edge((new_vertex2, edge.nodes[1]),
                                                       flow=edge.flow,
                                                       fields=edge.fields,
                                                       arrow=graph_state.Arrow(graph_state.Arrow.NULL),
                                                       marker=edge.marker,
                                                       external_node=graph.external_vertex))
        to_return = list()
        all_edges_3edges = map(lambda e: e.copy(arrow=graph_state.Arrow(graph_state.Arrow.NULL)) if e.arrow is None else e, all_edges_3edges)
        to_return.append((graphine.Graph(all_edges_3edges, external_vertex=graph.external_vertex), c2()))

        all_edges_2edges = copy.copy(graph.allEdges())
        edge = comb[0][0]
        all_edges_2edges.remove(edge)
        new_vertex = graph.createVertexIndex()
        all_edges_2edges.append(graph_util_mr.new_edge((edge.nodes[0], new_vertex),
                                                       flow=edge.flow,
                                                       fields=edge.fields,
                                                       external_node=graph.external_vertex))
        all_edges_2edges.append(graph_util_mr.new_edge((new_vertex, edge.nodes[1]),
                                                       flow=edge.flow,
                                                       fields=edge.fields,
                                                       external_node=graph.external_vertex))
        to_return.append((graphine.Graph(all_edges_2edges, external_vertex=graph.external_vertex), c3()))
        return to_return
    else:
        #
        # d_xi
        #
        all_edges = copy.copy(graph.allEdges())
        for c in comb:
            edge = c[0]
            all_edges.remove(edge)
            new_vertex = graph.createVertexIndex()
            numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW if comb[1] else graph_state.Arrow.RIGHT_ARROW)
            new_edge1 = graph_util_mr.new_edge((edge.nodes[0], new_vertex),
                                               external_node=graph.external_vertex,
                                               flow=edge.flow,
                                               fields=edge.fields,
                                               marker=edge.marker,
                                               arrow=numerator)
            new_edge2 = graph_util_mr.new_edge((new_vertex, edge.nodes[1]),
                                               external_node=graph.external_vertex,
                                               flow=edge.flow,
                                               fields=edge.fields,
                                               marker=edge.marker,
                                               arrow=graph_state.Arrow(graph_state.Arrow.NULL))
            all_edges.append(new_edge1)
            all_edges.append(new_edge2)
        all_edges = map(lambda e: e.copy(arrow=graph_state.Arrow(graph_state.Arrow.NULL)) if e.arrow is None else e, all_edges)
        new_graph = graphine.Graph(all_edges, external_vertex=graph.external_vertex)
        return [(new_graph, c1())]


def D_p2(graph):
    assert len(graph.edges(graph.external_vertex)) == 2
    minimal_passing = graphine.util.find_shortest_momentum_flow(graph)
    graph, minimal_passing = construct_graph_with_markers(graph, minimal_passing)
    return dict(reduce(lambda r, comb: r + _do_diff(graph, comb), itertools.combinations_with_replacement(minimal_passing, 2), list()))


def D_i_omega(graph):
    minimal_passing = graphine.util.find_shortest_momentum_flow(graph)
    graph, minimal_passing = construct_graph_with_markers(graph, minimal_passing)
    new_graphs = list()
    for e, sign in minimal_passing:
        new_edges = copy.copy(graph.allEdges())
        new_edges.remove(e)
        next_vertex = graph.createVertexIndex()
        new_edges.append(graph_util_mr.new_edge((e.nodes[0], next_vertex),
                                                external_node=graph.external_vertex,
                                                fields=e.fields,
                                                flow=e.flow))
        new_edges.append(graph_util_mr.new_edge((next_vertex, e.nodes[1]),
                                                external_node=graph.external_vertex,
                                                fields=e.fields,
                                                flow=e.flow))
        new_graphs.append(graphine.Graph(new_edges))
    return new_graphs


def D_minus_tau(graph):
    new_graphs = list()
    graph_edges = graph.allEdges()
    for e in graph.allEdges():
        if e.is_external():
            continue
        new_edges = copy.copy(graph_edges)
        new_edges.remove(e)
        next_vertex = graph.createVertexIndex()
        non_empty_arrow = e.arrow
        empty_arrow = None if non_empty_arrow is None else graph_state.Arrow(graph_state.Arrow.NULL)
        new_edges.append(graph_util_mr.new_edge((e.nodes[0], next_vertex),
                                                external_node=graph.external_vertex,
                                                fields=e.fields,
                                                flow=e.flow,
                                                marker=e.marker,
                                                arrow=non_empty_arrow))
        new_edges.append(graph_util_mr.new_edge((next_vertex, e.nodes[1]),
                                                external_node=graph.external_vertex,
                                                fields=e.fields,
                                                flow=e.flow,
                                                marker=e.marker,
                                                arrow=empty_arrow))
        new_graphs.append(graphine.Graph(new_edges))
    return new_graphs