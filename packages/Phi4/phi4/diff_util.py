#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import const
import graph_state
import graph_util

__author__ = 'dima'

from rggraphenv import symbolic_functions
import itertools
import const
import graphine
import inject


def c1():
    return inject.instance("space_dimension") / inject.instance("dimension")


def c2():
    d = inject.instance("dimension")
    return (inject.instance("space_dimension") - d) / d


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


def _find_minimal_external_momentum_passing(graph):
    """
    BFS
    """
    external_edges = graph.edges(graph.external_vertex)
    start_vertex = external_edges[0].internal_nodes[0]
    target_vertex = external_edges[1].internal_nodes[0]
    queue = [start_vertex]
    distances = {start_vertex: ()}
    while len(queue):
        vertex = queue[0]
        del queue[0]
        dist = distances.get(vertex)
        for e in graph.edges(vertex):
            if len(e.internal_nodes) == 1:
                continue
            v = e.nodes[1 if e.nodes[0] == vertex else 0]
            e_dist = distances.get(v)
            new_dist = 1 + len(dist)
            if e_dist is None or len(e_dist) > new_dist:
                #
                # optimization for fast work
                #
                if v == target_vertex and new_dist == 1:
                    return (e, e.nodes[0] == vertex),
                sign = e.nodes[0] == vertex
                distances[v] = dist + ((e, sign),)
                queue.append(v)
    return distances[target_vertex]


def _do_diff(graph, old_graph, comb):
    if comb[0] == comb[1]:
        #
        # (d_xi)^2
        #
        all_edges = copy.copy(old_graph.allEdges())
        edge = comb[0][1][0]
        all_edges.remove(edge)
        new_vertex = old_graph.createVertexIndex()
        all_edges.append(graph_util.new_edge((edge.nodes[0], new_vertex),
                                             weight=const.UNIT_WEIGHT,
                                             external_node=graph.external_vertex))
        all_edges.append(graph_util.new_edge((edge.nodes[1], new_vertex),
                                             weight=const.UNIT_WEIGHT,
                                             external_node=graph.external_vertex))
        return c2(), graphine.Graph(all_edges, external_vertex=graph.external_vertex, renumbering=False)
    else:
        #
        # d_xi
        #
        all_edges = copy.copy(graph.allEdges())
        for c in comb:
            edge = c[0][0]
            all_edges.remove(edge)
            new_vertex = graph.createVertexIndex()
            numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW if comb[1] else graph_state.Arrow.RIGHT_ARROW)
            new_edge1 = graph_util.new_edge((edge.nodes[0], new_vertex),
                                            external_node=graph.external_vertex,
                                            weight=const.UNIT_WEIGHT,
                                            arrow=numerator,
                                            marker=const.MARKER_1)
            new_edge2 = graph_util.new_edge((edge.nodes[1], new_vertex),
                                            weight=const.UNIT_WEIGHT,
                                            arrow=graph_state.Arrow(graph_state.Arrow.NULL),
                                            external_node=graph.external_vertex,
                                            marker=const.MARKER_1)
            all_edges.append(new_edge1)
            all_edges.append(new_edge2)
        all_edges = map(lambda e: e.copy(arrow=graph_state.Arrow(graph_state.Arrow.NULL)) if e.arrow is None else e, all_edges)
        return c1(), graphine.Graph(all_edges, external_vertex=graph.external_vertex, renumbering=False)


def diff_p2(graph):
    assert len(graph.edges(graph.external_vertex)) == 2
    minimal_passing = graphine.util.find_shortest_momentum_flow(graph)
    new_graph_edges = map(lambda e: e.copy(marker=const.MARKER_0), graph.allEdges())
    new_minimal_passing = list()
    for e, b in minimal_passing:
        new_graph_edges.remove(e.copy(marker=const.MARKER_0))
        new_e = e.copy(marker=const.MARKER_1)
        new_graph_edges.append(new_e)
        new_minimal_passing.append((new_e, b))
    new_graph = graphine.Graph(new_graph_edges, external_vertex=graph.external_vertex, renumbering=False)
    return map(lambda comb: _do_diff(new_graph, graph, comb), itertools.combinations_with_replacement(zip(new_minimal_passing, minimal_passing), 2))