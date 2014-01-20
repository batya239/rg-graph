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

D = const.SPACE_DIM_PHI4 - 2 * symbolic_functions.e

C1 = const.SPACE_DIM_PHI4 / D
C2 = (const.SPACE_DIM_PHI4 - D) / D


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
    external_edges = graph.edges(graph.externalVertex)
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


def _do_diff(graph, comb):
    all_edges = copy.copy(graph.allEdges())
    if comb[0] == comb[1]:
        #
        # (d_xi)^2
        #
        edge = comb[0][0]
        all_edges.remove(edge)
        new_vertex = graph.createVertexIndex()
        all_edges.append(graph_util.new_edge((edge.nodes[0], new_vertex),
                                             colors=const.ONE_LINE_WEIGHT,
                                             external_node=graph.externalVertex))
        all_edges.append(graph_util.new_edge((edge.nodes[1], new_vertex),
                                             colors=const.ONE_LINE_WEIGHT,
                                             external_node=graph.externalVertex))
        return C2, graphine.Graph(all_edges, externalVertex=graph.externalVertex, renumbering=False)
    else:
        #
        # d_xi
        #
        for c in comb:
            edge = c[0]
            all_edges.remove(edge)
            new_vertex = graph.createVertexIndex()
            numerator = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW if comb[1] else graph_state.Arrow.RIGHT_ARROW)
            new_edge1 = graph_util.new_edge((edge.nodes[0], new_vertex),
                                            external_node=graph.externalVertex,
                                            colors=const.ONE_LINE_WEIGHT,
                                            arrow=numerator)
            new_edge2 = graph_util.new_edge((edge.nodes[1], new_vertex),
                                            colors=const.ONE_LINE_WEIGHT,
                                            external_node=graph.externalVertex)
            all_edges.append(new_edge1)
            all_edges.append(new_edge2)
        all_edges = map(_init_edge_arrow, all_edges)
        return C1, graphine.Graph(all_edges, externalVertex=graph.externalVertex, renumbering=False)


def _init_edge_arrow(e):
    return e.copy(arrow=graph_state.Arrow(graph_state.Arrow.NULL)) if e.arrow is None else e


def diff_p2(graph):
    assert len(graph.edges(graph.externalVertex)) == 2
    minimal_passing = _find_minimal_external_momentum_passing(graph)
    return map(lambda comb: _do_diff(graph, comb), itertools.combinations_with_replacement(minimal_passing, 2))