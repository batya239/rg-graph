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

_irRelevanceCondition = graphine.phi4.IRRelevanceCondition()


def graphHasNotIRDivergence(graph):
    allEdges = graph.allEdges()
    for sg in graph.xRelevantSubGraphs(graphine.filters.connected, resultRepresentator=graphine.Representator.asGraph):
        if _irRelevanceCondition.isRelevant(sg.allEdges(withIndex=False), superGraph=graph, superGraphEdges=allEdges):
            return False

    return True


def doRPrime(graph, kOperation, uvSubGraphFilter, description=""):
    assert len(graph.edges(graph.externalVertex)) == 2

    if not graphHasNotIRDivergence(graph):
        raise AssertionError(str(graph) + " - IR divergence")

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
                shrinked, p2Counts = _doShrinkToPoint(graph, comb)
                rawRPrime += sign * kOperation.calculate(r1 * _calculateGraphValue(shrinked)) * (symbolic_functions.p2 ** p2Counts)

    result = symbolic_functions.polePart(rawRPrime)
    rprime_storage.putGraphR1(graph, result, GFUN_METHOD_NAME_MARKER, description)
    return result


def _doShrinkToPoint(graph, subGraphs):
    toShrink = list()
    p2Counts = 0
    excludedEdges = set()
    for sg in subGraphs:
        edge = _hasMomentumQuadraticDivergence(sg, graph, excludedEdges)
        if edge is not None:
            toShrink.append(graphine.Graph([edge], graph.externalVertex, renumbering=False))
            p2Counts += 1
        toShrink.append(sg)
    shrinked = graph.batchShrinkToPoint(toShrink)
    return shrinked, p2Counts


def _hasMomentumQuadraticDivergence(subGraph, graph, excludedEdges):
    externalEdges = subGraph.edges(subGraph.externalVertex)
    if len(externalEdges) != 2:
        return None
    nEdges = len(subGraph.allEdges()) - len(externalEdges)
    nVertexes = len(subGraph.vertexes()) - 1
    nLoop = nEdges - nVertexes + 1
    subgraphUVIndex = nEdges * (-2) + nLoop * 4
    if subgraphUVIndex != 2:
        return None

    borderVertexes = reduce(lambda x, y: x | y,
                            map(lambda x: set(x.nodes), subGraph.edges(subGraph.externalVertex))) - \
                            set([subGraph.externalVertex])

    for bv in borderVertexes:
        subGraphEdges = subGraph.edges(bv)
        graphEdges = graph.edges(bv)
        if len(subGraphEdges) == len(graphEdges):
            rawEdges = set(graphEdges) - set(subGraphEdges)
            if rawEdges not in externalEdges:
                assert len(rawEdges) == 1
                edge = list(rawEdges)[0]
                excludedEdges.add(edge)
                return edge

    assert False


def _calculateGraphsValues(graphs, suppressException=False):
    return reduce(lambda e, g: e * _calculateGraphValue(g, suppressException), graphs, 1)


def _calculateGraphValue(graph, suppressException=False):
    if len(graph.edges(graph.externalVertex)) == 2:
        graphReducer = subgraph_processer.GGraphReducer(graph)
    else:
        graphReducer = None
        for gWithMomentum in momentum.xPassExternalMomentum(graph, [graphHasNotIRDivergence]):
            graphReducer = subgraph_processer.GGraphReducer(gWithMomentum)
            break
        if graphReducer is None:
            raise CannotBeCalculatedError(graph)
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
