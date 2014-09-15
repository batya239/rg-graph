#!/usr/bin/python
# -*- coding: utf8
import rggraphutil

__author__ = 'daddy-bear'

import graph_state

import graphine
import graphine.filters as filters
import sys
import const
import inject


def uv_index(graph):
    index = denominator_dimension(graph) + numerators_count(graph.edges()) + graph.loops_count * inject.instance("space_dimension_int")
    return index


def denominator_dimension(graph):
    result = 0
    for e in graph.internal_edges:
        assert e.weight.b == 0, e
        result += e.weight.a
    return result * const.EDGE_WEIGHT


def numerators_count(edges_list):
    _numerators_count = 0
    for e in edges_list:
        if e.arrow is not None and not e.arrow.is_null():
            _numerators_count += 1
    return _numerators_count


class UVRelevanceCondition(object):
    def __init__(self, space_dim):
        self._space_dim = space_dim

    # noinspection PyUnusedLocal
    def is_relevant(self, edges_list, super_graph):
        assert_right_edges(edges_list, arbitrary_lines=True)

        sub_graph = graphine.Representator.asGraph(edges_list)
        sub_graph_uv_index = denominator_dimension(sub_graph) \
                             + numerators_count(edges_list) \
                             + sub_graph.loops_count * self._space_dim
        return sub_graph_uv_index >= 0


class IRRelevanceCondition(object):
    def __init__(self, space_dim):
        self._space_dim = space_dim

    def is_relevant(self, edges_list, super_edges):
        sub_graph = graphine.Representator.asGraph(edges_list)

        border_nodes = sub_graph.get_bound_vertices()
        if len(border_nodes) > 2:
            return False

        assert_right_edges(edges_list)
        sub_graph_ir_index = denominator_dimension(sub_graph) \
                             + numerators_count(edges_list) \
                             + (sub_graph.loops_count + 1) * self._space_dim
        # invalid result for e12-e333-3-- (there is no IR sub_graphs)
        if sub_graph_ir_index > 0:
            return False

        super_border_nodes = reduce(lambda x, y: x | y,
                                  map(lambda x: set(x.nodes), super_edges.edges(super_edges.external_vertex))) - \
                                  set([super_edges.external_vertex])

        connection_equivalence = _MergeResolver(super_edges.external_vertex, border_nodes, super_border_nodes)
        for e in super_edges.edges():
            connection_equivalence.add_edge(e)
        return connection_equivalence.is_relevant()


class _MergeResolver(object):
    def __init__(self, externalVertex, cutVertexes, superBorderNodes):
        self._disjoint_set = graph_state.operations_lib.DisjointSet()
        self._borders = rggraphutil.emptyListDict()
        self._connected_components = list()
        self._cut_vertexes = set(cutVertexes)
        self._external_vertex = externalVertex
        self._has_border_jumpers = False
        self._super_border_vertexes = superBorderNodes

    def add_edge(self, e):
        if self._has_border_jumpers:
            return
        vs = filter(lambda v: v not in self._cut_vertexes and v is not self._external_vertex, e.nodes)
        length = len(vs)
        if length == 0:
            if not self._has_border_jumpers and len(filter(lambda v: v is not self._external_vertex, e.nodes)) == 2:
                self._has_border_jumpers = True
        elif length == 1:
            self._disjoint_set.add_key(vs[0])
            border = filter(lambda v: v is not vs[0], e.nodes)[0]
            if border is not self._external_vertex:
                self._borders[vs[0]].append(border)
        else:
            #lenght = 2
            self._disjoint_set.union((vs[0], vs[1]))

    def is_relevant(self):
        if self._has_border_jumpers:
            return True
        components = self._disjoint_set.get_connected_components()
        if len(components) == 1:
            return True
        countWith2Tails = 0
        for component in components:
            borders = list()
            superBorderNodesCount = 0
            for v in component:
                if v in self._super_border_vertexes:
                    superBorderNodesCount += 1
                borders += self._borders[v]
            if len(set(borders)) == 2 or (len(borders) == 1 and superBorderNodesCount > 0):
                countWith2Tails += 1

        return countWith2Tails > 1


def assert_right_edges(edges, arbitrary_lines=False):
    for e in edges:
        if e.is_external():
            continue
        if e.weight:
            assert e.weight.b == 0, e
            assert arbitrary_lines or e.weight.a == 1, e
            assert isinstance(e.weight.a, int), e