#!/usr/bin/python
# -*- coding: utf8
import graphine
import const
import ir_uv
import inject
from rggraphenv import symbolic_functions
from rggraphutil import DisjointSet

__author__ = 'daddy-bear'


class CannotBeCalculatedError(StandardError):
    DEBUG = False

    def __init__(self, graph, reason=None):
        if reason is not None and CannotBeCalculatedError.DEBUG:
            print "Can't calculate %s, reason \"%s\"" % (graph, reason)
        self._graph = graph

    def __str__(self):
        return "cannot calculate " + str(self._graph)

    @classmethod
    def set_debug(cls, debug):
        CannotBeCalculatedError.DEBUG = debug


class T0OperationNotDefined(CannotBeCalculatedError):
    def __init__(self, graph):
        self._graph = graph

    def __str__(self):
        return "t0 not defined " + str(self._graph)


class AbstractKOperation(object):
    def calculate(self, graph):
        raise NotImplementedError


class MSKOperation(AbstractKOperation):
    def __init__(self, description="MS K-operation"):
        self._description = description

    def calculate(self, expression):
        return symbolic_functions.pole_part(expression, remove_order=False).expand().series(symbolic_functions.e == 0, 0)

    def __str__(self):
        return self._description

one_irreducible_and_no_tadpoles = graphine.filters.one_irreducible + graphine.filters.no_tadpoles


def graph_has_not_ir_divergence(graph):
    for _ in graph.x_relevant_sub_graphs(inject.instance("ir_filter")):
        return False
    return True


graph_has_not_ir_divergence_filter = [graph_has_not_ir_divergence]


def graph_can_be_calculated_over_n_loops(graph):
    """
    ololoshki
    """
    assert graph.external_edges_count == 2
    disjoint_set = DisjointSet(graph.get_bound_vertices() | set([graph.external_vertex]))
    for e in graph.edges():
        n1, n2 = e.nodes
        disjoint_set.union(n1, n2)
    connected_vertices = disjoint_set.get_sets()
    max_loops = 0
    for vertices in connected_vertices:
        edges = list()
        for e in graph.edges():
            if len(set(e.nodes) & vertices):
                edges.append(e)
        g = graphine.Graph(edges)
        if g.loops_count > max_loops:
            max_loops = g.loops_count
    return max_loops
