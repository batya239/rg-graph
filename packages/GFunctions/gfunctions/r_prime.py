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

    def calculate(self, expression):
        return symbolic_functions.polePart(expression)


def doRPrime(graph, kOperation, uvSubGraphFilter, description=""):
    rprime_storage.checkInitialized()
    return _doRPrime(graph, kOperation, uvSubGraphFilter, description)


def _doRPrime(graph, kOperation, uvSubGraphFilter, description=""):
    evaluated = rprime_storage.getR1(graph)
    if evaluated is not None:
        for e in evaluated:
            return e[0]

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
                r1 = reduce(lambda e, g: e * _doRPrime(g, kOperation, uvSubGraphFilter), comb, 1)
                rawRPrime += sign * kOperation.calculate(r1 * _calculateGraphValue(graph.batchShrinkToPoint(comb)))

    result = symbolic_functions.polePart(rawRPrime)
    rprime_storage.putGraphR1(graph, result, GFUN_METHOD_NAME_MARKER, description)
    return result


def _calculateGraphsValues(graphs, suppressException=False):
    return reduce(lambda e, g: e * _calculateGraphValue(g, suppressException), graphs, 1)


def _calculateGraphValue(graph, suppressException=False):
    if len(graph.edges(graph.externalVertex)) == 2:
        graphReducer = subgraph_processer.GGraphReducer(graph)
    else:
        graphReducer = None
        for gWithMomentum in momentum.xPassExternalMomentum(graph):
            graphReducer = subgraph_processer.GGraphReducer(gWithMomentum)
            break
        if graphReducer is None:
            raise CannotBeCalculatedError
    while graphReducer.nextIteration():
        pass
    if not graphReducer.isSuccesfulDone():
        if suppressException:
            return None
        else:
            raise CannotBeCalculatedError(graph)
    finalValue = graphReducer.getFinalValue()
    evaluated = symbolic_functions.evaluate(finalValue[0], finalValue[1])
    return evaluated


def _hasIntersectingSubGraphs(subGraphs):
    if not len(subGraphs):
        return False
    uniqueVertexes = set()
    for g in subGraphs:
        internalVertexes = g.vertexes() - set([g.externalVertex])
        currentUniqueVertexesSize = len(uniqueVertexes)
        uniqueVertexes |= internalVertexes
        if len(uniqueVertexes) != currentUniqueVertexesSize + len(internalVertexes):
            return True
    return False
