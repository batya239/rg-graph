#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import graph_state

import const
import graph_util


__author__ = 'dima'

import itertools
import const
import graphine
import inject
import swiginac
import collections
import graph_util
from rggraphenv.symbolic_functions import CLN_ZERO, CLN_TWO, CLN_ONE, cln, e

CLN_FOUR = swiginac.numeric("4")


def dalembertian_coefficient(a=1, b=None):
    assert b is not None
    a = cln(a)
    b = cln(b)
    return CLN_ONE / CLN_TWO * ((a + b * e) * (CLN_TWO + CLN_FOUR / inject.instance("dimension") * (a - CLN_ONE + b * e)))


def c1():
    return CLN_FOUR / inject.instance("dimension")


def c2():
    d = inject.instance("dimension")
    return (CLN_FOUR - d) / d


def factorized_c2():
    d = inject.instance("dimension")
    if d.subs(e == CLN_ZERO).is_equal(CLN_FOUR):
        return True, ((CLN_FOUR - d) / e).expand() / d
    else:
        return False, (CLN_FOUR - d).expand() / d


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


# def _do_diff(graph, old_graph, comb):
#     all_edges = list(old_graph.edges())
#     new_vertex = old_graph.create_vertex_index()
#     if comb[0] == comb[1]:
#         #
#         # (d_xi)^2
#         #
#         edge = comb[0][1][0]
#         all_edges.remove(edge)
#         all_edges.append(graph_util.new_edge((edge.nodes[0], new_vertex),
#                                              weight=const.UNIT_WEIGHT,
#                                              external_node=graph.external_vertex))
#         all_edges.append(graph_util.new_edge((edge.nodes[1], new_vertex),
#                                              weight=const.UNIT_WEIGHT,
#                                              external_node=graph.external_vertex))
#         return c2(), graphine.Graph(all_edges, renumbering=False)
#     else:
#         #
#         # d_xi
#         #
#         for c in comb:
#             edge = c[1][0]
#             try:
#                 all_edges.remove(edge)
#             except ValueError as e:
#                 print edge, all_edges
#                 raise e
#             numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW if comb[1] else graph_state.Arrow.RIGHT_ARROW)
#             new_edge1 = graph_util.new_edge((edge.nodes[0], new_vertex),
#                                             external_node=graph.external_vertex,
#                                             weight=const.UNIT_WEIGHT,
#                                             arrow=numerator,
#                                             marker=const.MARKER_1)
#             new_edge2 = graph_util.new_edge((edge.nodes[1], new_vertex),
#                                             weight=const.UNIT_WEIGHT,
#                                             arrow=graph_state.Arrow(graph_state.Arrow.NULL),
#                                             external_node=graph.external_vertex,
#                                             marker=const.MARKER_1)
#             all_edges.append(new_edge1)
#             all_edges.append(new_edge2)
#         all_edges = map(lambda e: e.copy(arrow=graph_state.Arrow(graph_state.Arrow.NULL)) if e.arrow is None else e,
#                         all_edges)
#         return c1(), graphine.Graph(all_edges, renumbering=False)


def _do_diff(base_graph_edges, old_graph, comb):
    all_edges = list(old_graph.edges())
    new_vertex = old_graph.create_vertex_index()
    if comb[0] == comb[1]:
        #
        # (d_xi)^2
        #
        edge = comb[0][1][0]
        all_edges.remove(edge)
        all_edges.append(graph_util.new_edge((edge.nodes[0], new_vertex),
                                             weight=const.UNIT_WEIGHT,
                                             external_node=old_graph.external_vertex))
        all_edges.append(graph_util.new_edge((edge.nodes[1], new_vertex),
                                             weight=const.UNIT_WEIGHT,
                                             external_node=old_graph.external_vertex))
        return c2(), graphine.Graph(all_edges, renumbering=False)
    else:
        #
        # d_xi
        #
        for c in comb:
            edge = c[1][0]
            try:
                all_edges.remove(edge)
            except ValueError as e:
                print edge, all_edges
                raise e
            numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW if comb[1] else graph_state.Arrow.RIGHT_ARROW)
            new_edge1 = graph_util.new_edge((edge.nodes[0], new_vertex),
                                            external_node=old_graph.external_vertex,
                                            weight=const.UNIT_WEIGHT,
                                            arrow=numerator,
                                            marker=const.MARKER_1)
            new_edge2 = graph_util.new_edge((edge.nodes[1], new_vertex),
                                            weight=const.UNIT_WEIGHT,
                                            arrow=graph_state.Arrow(graph_state.Arrow.NULL),
                                            external_node=old_graph.external_vertex,
                                            marker=const.MARKER_1)
            all_edges.append(new_edge1)
            all_edges.append(new_edge2)
        all_edges = map(lambda e: e.copy(arrow=graph_state.Arrow(graph_state.Arrow.NULL)) if e.arrow is None else e,
                        all_edges)
        return c1(), graphine.Graph(all_edges, renumbering=False)

def diff_p2(graph):
    assert graph.external_edges_count == 2
    minimal_passing = graphine.util.find_shortest_momentum_flow(graph)
    new_graph_edges = map(lambda e: e.copy(marker=const.MARKER_0), graph.edges())
    new_minimal_passing = list()
    for e, b in minimal_passing:
        new_graph_edges.remove(e.copy(marker=const.MARKER_0))
        new_e = e.copy(marker=const.MARKER_1)
        new_graph_edges.append(new_e)
        new_minimal_passing.append((new_e, b))
    new_graph = graphine.Graph(new_graph_edges, renumbering=False)
    return map(lambda comb: _do_diff(new_graph, graph, comb),
               itertools.combinations_with_replacement(zip(new_minimal_passing, minimal_passing), 2))


def diff_single_propagator(base_graph_edges, edge, new_vertex_index):
    edges = list(base_graph_edges)
    edges.remove(edge)

    do_insert_eps, coefficient = factorized_c2()
    if do_insert_eps:
        new_vertex = graph_util.new_node(new_vertex_index, factor=graph_util.Factor(e))
    else:
        raise AssertionError("not implemented action 4-d !~ eps")

    edges.append(graph_util.new_edge((edge.nodes[0], new_vertex),
                                      weight=const.UNIT_WEIGHT,
                                      external_node=edge.external_node))
    edges.append(graph_util.new_edge((edge.nodes[1], new_vertex),
                                      weight=const.UNIT_WEIGHT,
                                      external_node=edge.external_node))
    return graphine.Graph(edges, renumbering=False), coefficient


def diff_two_propagators(base_graph_edges, diff_edges_and_directions, new_vertex_indices):
    edges = list(base_graph_edges)
    assert len(edges) == 2
    assert len(directions) == 2
    assert len(new_vertex_indices) == 2
    for (edge, direction), new_vertex_index in itertools.izip(diff_edges_and_directions, new_vertex_indices):
        edges.remove(edge)
        numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW if direction else graph_state.Arrow.RIGHT_ARROW)
        new_edge = graph_util.new_edge(edge.nodes,
                                        external_node=edge.external_node,
                                        weight=const.DOUBLE_WEIGHT_WEIGHT,
                                        arrow=numerator,
                                        marker=const.MARKER_1)
        edges.append(new_edge)
    return graphine.Graph(edges, renumbering=False), c1()


def dalembertian(graph):
    assert graph.external_edges_count == 2

    momentum_passing = graphine.util.find_shortest_momentum_flow(graph)
    result = collections.defaultdict(lambda: CLN_ZERO)
    new_vertex_index_1 = graph.create_vertex_index()
    for e, _ in momentum_passing:
        graph, c = diff_single_propagator(graph.edges(), e, new_vertex_index_1)
        result[graph] += c

    if len(momentum_passing) > 1:
        marked_graph_edges = list(graph.edges())
        marked_momentum_passing = list()
        for e, b in momentum_passing:
            marked_graph_edges.remove(e)
            new_e = e.copy(marker=const.MARKER_1)
            marked_graph_edges.append(new_e)
            marked_momentum_passing.append((new_e, b))

        new_vertex_indices = (new_vertex_index_1, graph.create_vertex_index())
        for comb in itertools.combinations(marked_momentum_passing, 2):
            graph, c = diff_single_propagator(marked_graph_edges, comb, new_vertex_indices)
            result[graph] += c

    return result.items()

