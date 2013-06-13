#!/usr/bin/python
# -*- coding: utf8
import itertools

__author__ = 'daddy-bear'

import symbolic_functions
import graphine.phi4
import subgraph_processer
import rprime_storage


class RPrimeCannotBeCalculatedError(AssertionError):
    pass


GFUN_METHOD_NAME_MARKER = "g-functions"
MS_SCHEME_NAME_MARKER = "ms-scheme"

_subgraphUVFilters = (graphine.filters.oneIrreducible
                      + graphine.filters.noTadpoles
                      + graphine.filters.isRelevant(graphine.phi4.UVRelevanceCondition()))


class AbstractKOperation(object):
    def calculateKOperation(self, graph):
        raise NotImplementedError


class MSKOperation(AbstractKOperation):
    def __init__(self, description=""):
        self._description = description

    def calculateKOperation(self, graph):
        evaluated = rprime_storage.getK(graph)
        if evaluated:
            for e in evaluated:
                if e[1] == MS_SCHEME_NAME_MARKER:
                    return e
        else:
            value = _calculateGraphValue(graph, onlyPolePart=True)
            rprime_storage.putGraphK(graph, value, MS_SCHEME_NAME_MARKER, self._description)
            return value


def doRPrime(graph, kOperation, description=""):
    """
    function NOT checks that incomplete R operation available for this graph
    """
    evaluated = rprime_storage.getR1(graph)
    if evaluated is not None:
        return evaluated

    uvSubgraphs = graphine.Graph.batchInitEdgesColors([sg for sg in graph.xRelevantSubGraphs(_subgraphUVFilters)])
    if not len(uvSubgraphs):
        result = symbolic_functions.polePart(_calculateGraphValue(graph))
        rprime_storage.putGraphR1(graph, result, GFUN_METHOD_NAME_MARKER, description)
        return result

    rawRPrime = _calculateGraphValue(graph)
    sign = 1
    for i in xrange(1, len(uvSubgraphs) + 1):
        sign *= -1
        for comb in itertools.combinations(uvSubgraphs, i):
            if not _hasIntersectingSubGraphs(comb):
                rawRPrime += sign * reduce(lambda g, e: kOperation.calculateKOperation(g) * e, comb, 1) * doRPrime(graph.batchShrinkToPoint(comb))

    result = symbolic_functions.polePart(rawRPrime)
    rprime_storage.putGraphR1(graph, result, GFUN_METHOD_NAME_MARKER, description)
    return result


def _calculateGraphsValues(graphs, onlyPolePart=False):
    result = 0
    for g in graphs:
        result *= _calculateGraphValue(g, onlyPolePart)
    return result


def _calculateGraphValue(graph, onlyPolePart=False):
    graphReducer = subgraph_processer.GGraphReducer(graph)
    while graphReducer.nextIteration():
        pass
    if not graphReducer.isSuccesfulDone():
        raise RPrimeCannotBeCalculatedError
    finalValue = graphReducer.getFinalValue()
    return symbolic_functions.evaluateSeries(finalValue[0], finalValue[1], onlyPolePart)


def _hasIntersectingSubGraphs(subGraphs):
    if not len(subGraphs):
        return False
    uniqueEdges = set()
    for g in subGraphs:
        currentEdges = set(g.allEdges(withIndex=True))
        currentUniqueEdgesLength = len(uniqueEdges)
        uniqueEdges |= currentEdges
        if currentUniqueEdgesLength + len(currentEdges) != len(uniqueEdges):
            return True
    return False
