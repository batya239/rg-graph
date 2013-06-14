#!/usr/bin/python
# -*- coding: utf8
import itertools

__author__ = 'daddy-bear'

import symbolic_functions
import graphine.phi4
import subgraph_processer
import rprime_storage
import momentum


class CannotBeCalculatedError(AssertionError):
    pass


GFUN_METHOD_NAME_MARKER = "g-functions"
MS_SCHEME_NAME_MARKER = "ms-scheme"

defaultSubgraphUVFilter = (graphine.filters.oneIrreducible
                      + graphine.filters.noTadpoles
                      + graphine.filters.isRelevant(graphine.phi4.UVRelevanceCondition()))


class AbstractKOperation(object):
    def calculate(self, graph):
        raise NotImplementedError


class MSKOperation(AbstractKOperation):
    def __init__(self, description=""):
        self._description = description

    def calculate(self, graph):
        for gWithMomentum in momentum.xPassExternalMomentum(graph):
            evaluated = rprime_storage.getK(gWithMomentum)
            if evaluated:
                for e in evaluated:
                    if e[1] == MS_SCHEME_NAME_MARKER:
                        return e[0]
            value = _calculateGraphValue(gWithMomentum, onlyPolePart=True, suppressException=True)
            if value is not None:
                rprime_storage.putGraphK(gWithMomentum, value, MS_SCHEME_NAME_MARKER, self._description)
                return value
        raise CannotBeCalculatedError(graph)


def doRPrime(graph, kOperation, uvSubGraphFilter, description=""):
    rprime_storage.checkInitialized()
    return _doRPrime(graph, kOperation, uvSubGraphFilter, description)


def _doRPrime(graph, kOperation, uvSubGraphFilter, description=""):
    evaluated = rprime_storage.getR1(graph)
    if evaluated is not None:
        return evaluated[0]

    uvSubgraphs = graphine.Graph.batchInitEdgesColors([sg for sg in graph.xRelevantSubGraphs(uvSubGraphFilter)])
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
                rawRPrime += sign * reduce(lambda e, g: kOperation.calculate(g) * e, comb, 1) * _doRPrime(
                    graph.batchShrinkToPoint(comb), kOperation)

    result = symbolic_functions.polePart(rawRPrime)
    rprime_storage.putGraphR1(graph, result, GFUN_METHOD_NAME_MARKER, description)
    return result


def _calculateGraphsValues(graphs, onlyPolePart=False):
    result = 0
    for g in graphs:
        result *= _calculateGraphValue(g, onlyPolePart)
    return result


def _calculateGraphValue(graph, onlyPolePart=False, suppressException=False):
    graphReducer = subgraph_processer.GGraphReducer(graph)
    while graphReducer.nextIteration():
        pass
    if not graphReducer.isSuccesfulDone():
        if suppressException:
            return None
        else:
            raise CannotBeCalculatedError
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