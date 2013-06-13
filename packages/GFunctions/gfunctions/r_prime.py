#!/usr/bin/python
# -*- coding: utf8
import itertools

__author__ = 'daddy-bear'

import symbolic_functions
import graphine.phi4
import subgraph_processer


class RPrimeCannotBeCalculatedError(AssertionError):
    pass


_subgraphUVFilters = (graphine.filters.oneIrreducible
                      + graphine.filters.noTadpoles
                      + graphine.filters.vertexIrreducible
                      + graphine.filters.isRelevant(graphine.phi4.UVRelevanceCondition()))


def doRPrime(graph):
    """
    function NOT checks that incomplete R operation available for this graph
    """
    uvSubgraphs = graphine.Graph.batchInitEdgesColors([sg for sg in graph.xRelevantSubGraphs(_subgraphUVFilters)])
    if not len(uvSubgraphs):
        return symbolic_functions.polePart(_calculateGraphValue(graph))

    rawRPrime = _calculateGraphValue(graph)
    sign = 1
    for i in xrange(1, len(uvSubgraphs) + 1):
        sign *= -1
        for comb in itertools.combinations(uvSubgraphs, i):
            if not _hasIntersectingSubGraphs(comb):
                rawRPrime += sign * _calculateGraphsValues(comb) * doRPrime(graph.batchShrinkToPoint(comb))

    return symbolic_functions.polePart(rawRPrime)


def _calculateGraphsValues(graphs):
    result = 0
    for g in graphs:
        result *= _calculateGraphValue(g)
    return result


def _calculateGraphValue(graph):
    graphReducer = subgraph_processer.GGraphReducer(graph)
    while graphReducer.nextIteration():
        pass
    if not graphReducer.isSuccesfulDone():
        raise RPrimeCannotBeCalculatedError
    finalValue = graphReducer.getFinalValue()
    return symbolic_functions.evaluateSeries(finalValue[0], finalValue[1])


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
