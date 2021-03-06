#!/usr/bin/python
# -*- coding: utf8
import graph_util

__author__ = 'dima'

import reduction
import common
import const
from rggraphenv import graph_calculator


def scalar_product_extractor(topology, graph):
    extracted_numerated_edges = list()
    for e1, e2 in zip(topology.edges(nickel_ordering=True), graph.edges(nickel_ordering=True)):
        numerator = e2.arrow if (e2.arrow is not None and not e2.arrow.is_null()) else None
        if numerator:
            extracted_numerated_edges.append((e1, numerator))
    if not len(extracted_numerated_edges):
        raise StopIteration()
    if len(extracted_numerated_edges) == 1:
        numerated_edge = extracted_numerated_edges[0]
        sign = -1 if numerated_edge[1].is_left() else 1
        sp = reduction.ScalarProduct(numerated_edge[0].weight[1],
                                     (1, ) + (0, ) * (len(numerated_edge[0].weight[1]) - 1),
                                     sign=sign)
        yield sp
    else:
        assert len(extracted_numerated_edges) == 2, ("graph must has only 2 numerated edges, actual = %s, graph = %s" % (extracted_numerated_edges, graph))
        raw_common_vertex = set(extracted_numerated_edges[0][0].nodes) & set(extracted_numerated_edges[1][0].nodes)
        if not len(raw_common_vertex):
            sign = resolve_scalar_product_sign(graph, extracted_numerated_edges)
        else:
            common_vertex = raw_common_vertex.pop()
            if common_vertex in graph.get_bound_vertices():
                raise common.CannotBeCalculatedError(graph)
            adjusted_numerators = map(lambda (e, n): n if e.nodes[0] == common_vertex else -n, extracted_numerated_edges)
            sign = 1 if adjusted_numerators[0] != adjusted_numerators[1] else -1
            if extracted_numerated_edges[0][0].nodes.index(common_vertex) == extracted_numerated_edges[1][0].nodes.index(common_vertex):
                sign *= -1

        sp = reduction.ScalarProduct(extracted_numerated_edges[0][0].weight[1],
                                     extracted_numerated_edges[1][0].weight[1],
                                     sign=sign)
        yield sp


def resolve_scalar_product_sign(graph, extracted_numerated_edges):
    bound_vertices = graph.getBoundVertexes()
    momentum_passing = map(lambda e: e.nodes, filter(lambda e: not e.is_external() and e.marker == const.MARKER_1, graph.allEdges()))
    momentum_passing.remove(extracted_numerated_edges[0][0].nodes)
    for j in xrange(2):
        current_node = extracted_numerated_edges[0][0].nodes
        current_vertex = current_node[j]
        sign = (1 if extracted_numerated_edges[0][1].is_left() else -1) * ((-1) ** j)
        while True:
            nodes_found = False
            if current_vertex in bound_vertices:
                raise common.CannotBeCalculatedError(graph)
            for n in momentum_passing:
                if n != current_node and current_vertex in n:
                    current_node = n

                    current_vertex = filter(lambda i: i != current_vertex, current_node)[0]
                    momentum_passing.remove(current_node)
                    nodes_found = True
                    break
            if not nodes_found:
                break
            if current_node == extracted_numerated_edges[1][0].nodes:
                sign *= (1 if extracted_numerated_edges[1][1].is_left() else -1)
                sign *= 1 if current_vertex == current_node[0] else -1
                return sign


def weight_extractor(edge):
    w = edge.weight
    if w is None or w.b != 0:
        return None
    return w.a


def create_calculator(*loops_counts):
    return reduction.ScalarProductReductionGraphCalculator(weight_extractor, scalar_product_extractor, loops_counts)

GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR = reduction.ScalarProductReductionGraphCalculator(weight_extractor, scalar_product_extractor)