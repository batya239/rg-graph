#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import itertools
import graphine
import graph_state
import copy
import graphine
import graph_util_mr
import momentum_enumeration
import swiginac
import configure_mr

CLN_FOUR = swiginac.numeric("4")


def c1():
    return CLN_FOUR / configure_mr.Configure.dimension()


def c2():
    d = configure_mr.Configure.dimension()
    return (CLN_FOUR - d) / d


def initial_graph_edge_transformation(graph):
    new_edges = list()
    for e in graph.allEdges():
        if e.fields == graph_util_mr.aa:
            next_vertex = graph.createVertexIndex()
            new_edges.append(e.copy({e.nodes[1]: next_vertex}, fields=graph_util_mr.aA))
            new_edges.append(e.copy({e.nodes[0]: next_vertex}, fields=graph_util_mr.Aa))
        else:
            new_edges.append(e)
    return graphine.Graph(new_edges)


class ScalarProduct(object):
    def __init__(self, edge1, edge2):
        self._edge1 = edge1
        self._edge2 = edge2

    @property
    def edge1(self):
        return self._edge1

    @property
    def edge2(self):
        return self._edge2

    def __eq__(self, other):
        assert isinstance(other, ScalarProduct)
        return set((self.edge1, self.edge2)) == set((other.edge1, other.edge2))

    def __hash__(self):
        return hash(frozenset((self.edge1, self.edge2)))


def enumerate_propagators(graph):
    enumerated_flows_graph = momentum_enumeration.choose_minimal_momentum_flow(graph)
    transformed_graph = initial_graph_edge_transformation(enumerated_flows_graph)
    with_propagators_graph = momentum_enumeration.attach_propagators(transformed_graph, has_mass=True)
    return with_propagators_graph


def get_internal_momentas(graph):
    return reduce(lambda s, e: s | e.flows.loop_momentas(), graph.allEdges(), set())


