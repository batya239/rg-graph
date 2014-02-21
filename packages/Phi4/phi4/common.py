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
    def __init__(self, graph):
        self._graph = graph

    def __str__(self):
        return "cannot calculate " + str(self._graph)


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
        return symbolic_functions.pole_part(expression)

    def __str__(self):
        return self._description

one_irreducible_and_no_tadpoles = graphine.filters.oneIrreducible + graphine.filters.noTadpoles

_DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT = dict()


def graph_has_not_ir_divergence(graph):
    result = _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT.get(graph, None)
    if result is None:
        for _ in graph.xRelevantSubGraphs(inject.instance("ir_filter")):
            _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT[graph] = False
            return False
        _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT[graph] = True
        return True
    return result

graph_has_not_ir_divergence_filter = [graph_has_not_ir_divergence]


def isPSquareGraph(graph):
    return graph.getLoopsCount() * const.SPACE_DIM_PHI4 - 2 * graph.getAllInternalEdgesCount() == 2


def graph_can_be_calculated_over_n_loops(graph):
    """
    ololoshki
    """
    assert graph.externalEdgesCount() == 2
    disjoint_set = DisjointSet(graph.getBoundVertexes() | set([graph.external_vertex]))
    for e in graph.allEdges():
        n1, n2 = e.nodes
        disjoint_set.union(n1, n2)
    connected_vertices = disjoint_set.get_sets()
    max_loops = 0
    for vertices in connected_vertices:
        edges = list()
        for e in graph.allEdges():
            if len(set(e.nodes) & vertices):
                edges.append(e)
        g = graphine.Graph(edges, external_vertex=graph.external_vertex)
        if g.getLoopsCount() > max_loops:
            max_loops = g.getLoopsCount()
    return max_loops
