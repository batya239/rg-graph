#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import const
import graph_state
import reduction

__author__ = 'dima'

from rggraphenv import symbolic_functions
import itertools

D = const.SPACE_DIM_PHI4 - 2 * symbolic_functions.e

C1 = const.SPACE_DIM_PHI4 / D
C2 = (const.SPACE_DIM_PHI4 - D) / D


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
                # hack for fast
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
        all_edges.append(graph_state.Edge((edge.nodes[0], new_vertex),
                                          colors=const.ONE_LINE_WEIGHT,
                                          external_node=graph.externalVertex))
        all_edges.append(graph_state.Edge((edge.nodes[1], new_vertex),
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
            numerator = const.LEFT_NUMERATOR if comb[1] else const.RIGHT_NUMERATOR
            new_edge1 = graph_state.Edge((edge.nodes[0], new_vertex),
                                         external_node=graph.externalVertex,
                                         colors=const.ONE_LINE_WEIGHT,
                                         fields=numerator)
            new_edge2 = graph_state.Edge((edge.nodes[1], new_vertex),
                                         colors=const.ONE_LINE_WEIGHT,
                                         external_node=graph.externalVertex)
            all_edges.append(new_edge1)
            all_edges.append(new_edge2)
        all_edges = map(_init_edge_fields, all_edges)
        return C1, graphine.Graph(all_edges, externalVertex=graph.externalVertex, renumbering=False)


def _init_edge_fields(e):
    return e.copy(fields=const.EMPTY_NUMERATOR) if e.fields is None else e


def diff_p2(graph):
    assert len(graph.edges(graph.externalVertex)) == 2
    minimal_passing = _find_minimal_external_momentum_passing(graph)
    return map(lambda comb: _do_diff(graph, comb), itertools.combinations_with_replacement(minimal_passing, 2))


def scalar_product_extractor(topology, graph):
    extracted_numerated_edges = list()

    for e1, e2 in zip(topology.allEdges(nickel_ordering=True), graph.allEdges(nickel_ordering=True)):
        if e2.fields is None:
            raise StopIteration()
        numerator = e2.fields if e2.fields == const.LEFT_NUMERATOR or e2.fields == const.RIGHT_NUMERATOR else None
        if numerator:
            extracted_numerated_edges.append((e1, numerator))

    assert len(extracted_numerated_edges) == 2, "graph must has only 2 numerated edges"
    common_vertex = (set(extracted_numerated_edges[0][0].nodes) & set(extracted_numerated_edges[1][0].nodes)).pop()
    adjusted_numerators = map(lambda (e, n): n if e.nodes[0] == common_vertex else -n, extracted_numerated_edges)
    sign = -1 if adjusted_numerators[0] == adjusted_numerators[1] else 1

    yield reduction.ScalarProduct(extracted_numerated_edges[0].colors[1],
                                  extracted_numerated_edges[1].colors[1], sign=sign)




