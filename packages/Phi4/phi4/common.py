#!/usr/bin/python
# -*- coding: utf8
import graphine
import const
import ir_uv
from rggraphenv import symbolic_functions

__author__ = 'daddy-bear'


class CannotBeCalculatedError(AssertionError):
    def __init__(self, graph):
        self._graph = graph

    def __str__(self):
        return "cannot calculate " + str(self._graph)


class T0OperationNotDefined(AssertionError):
    def __init__(self, graph):
        self._graph = graph

    def __str__(self):
        return "t0 not defined " + str(self._graph)


class AbstractKOperation(object):
    def calculate(self, graph):
        raise NotImplementedError


class MSKOperation(AbstractKOperation):
    def __init__(self, description=""):
        self._description = description

    def calculate(self, expression):
        #TODO fix
        return symbolic_functions.pole_part(expression).series(symbolic_functions.e == 0, 0).convert_to_poly(no_order=True)

MS_K_OPERATION = MSKOperation()

GFUN_METHOD_NAME_MARKER = "g-functions"
MS_SCHEME_NAME_MARKER = "ms-scheme"

defaultSubgraphUVFilter = graphine.filters.isRelevant(ir_uv.UV_RELEVANCE_CONDITION_4_DIM)

oneIrreducibleAndNoTadpoles = graphine.filters.oneIrreducible + graphine.filters.noTadpoles

_DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT = dict()

DEFAULT_IR_RELEVANCE = graphine.filters.isRelevant(ir_uv.IR_RELEVANCE_CONDITION_4_DIM)

subgraphIRFilters = (graphine.filters.connected + DEFAULT_IR_RELEVANCE)


def defaultGraphHasNotIRDivergence(graph):
    result = _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT.get(graph, None)
    if result is None:
        for _ in graph.xRelevantSubGraphs(subgraphIRFilters):
            _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT[graph] = False
            return False
        _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT[graph] = True
        return True
    return result

defaultGraphHasNotIRDivergenceFilter = [defaultGraphHasNotIRDivergence]


def isPSquareGraph(graph):
    return graph.getLoopsCount() * const.SPACE_DIM_PHI4 - 2 * graph.getAllInternalEdgesCount() == 2