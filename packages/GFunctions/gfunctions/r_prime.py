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


_DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT = dict()


def _defaultGraphHasNotIRDivergence(graph):
    result = _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT.get(graph, None)
    if result is None:
        allEdges = graph.allEdges()
        for sg in graph.xRelevantSubGraphs(graphine.filters.connected, resultRepresentator=graphine.Representator.asGraph):
            if _irRelevanceCondition.isRelevant(sg.allEdges(withIndex=False), superGraph=graph, superGraphEdges=allEdges):
                _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT[graph] = False
                return False
        _DEFAULT_GRAPH_HAS_NOT_IR_DIVERGENCE_RESULT[graph] = True
        return True
    return result

defaultGraphHasNotIRDivergenceFilter = [_defaultGraphHasNotIRDivergence]


def doRPrime(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True):
    assert len(graph.edges(graph.externalVertex)) == 2

    if not _defaultGraphHasNotIRDivergence(graph):
        raise AssertionError(str(graph) + " - IR divergence")

    rprime_storage.checkInitialized()
    return _doRPrime(graph, kOperation, uvSubGraphFilter, description=description, useGraphCalculator=useGraphCalculator)


def _doRPrime(rawGraph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True):
    for graph in momentum.xPassExternalMomentum(rawGraph, defaultGraphHasNotIRDivergenceFilter):

        evaluated = rprime_storage.getR1(graph)
        if evaluated is not None:
            for e in evaluated:
                return e[0]

        uvSubgraphs = graphine.Graph.batchInitEdgesColors([sg for sg in graph.xRelevantSubGraphs(uvSubGraphFilter)])
        if not len(uvSubgraphs):
            expression, twoTailsGraph = _calculateGraphValue(graph, useGraphCalculator=useGraphCalculator)
            pole_part = symbolic_functions.polePart(expression)
            rprime_storage.putGraphR1(twoTailsGraph, pole_part, GFUN_METHOD_NAME_MARKER, description)
            return pole_part

        rawRPrime = _calculateGraphValue(graph, useGraphCalculator=useGraphCalculator)[0]
        sign = 1
        for i in xrange(1, len(uvSubgraphs) + 1):
            sign *= -1
            for comb in itertools.combinations(uvSubgraphs, i):
                if not _hasIntersectingSubGraphs(comb):
                    r1 = reduce(lambda e, g: e * _doRPrime(g, kOperation, uvSubGraphFilter, useGraphCalculator=useGraphCalculator), comb, 1)
                    shrinked, p2Counts = _doShrinkToPoint(graph, comb)
                    rawRPrime += sign * kOperation.calculate(r1 * _calculateGraphValue(shrinked, useGraphCalculator=useGraphCalculator)[0]) * (symbolic_functions.p2 ** p2Counts)

        result = symbolic_functions.polePart(rawRPrime)
        rprime_storage.putGraphR1(graph, result, GFUN_METHOD_NAME_MARKER, description)
        return result
    raise CannotBeCalculatedError(rawGraph)

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


def _calculateGraphsValues(graphs, suppressException=False, useGraphCalculator=False):
    return reduce(lambda e, g: e * _calculateGraphValue(g, suppressException, useGraphCalculator=useGraphCalculator)[0], graphs, 1)


def _calculateGraphValue(graph, suppressException=False, useGraphCalculator=False):
    if len(graph.edges(graph.externalVertex)) == 2:
        graphReducer = subgraph_processer.GGraphReducer(graph, useGraphCalculator=useGraphCalculator)
    else:
        graphReducer = None
        for gWithMomentum in momentum.xPassExternalMomentum(graph, defaultGraphHasNotIRDivergenceFilter):
            graphReducer = subgraph_processer.GGraphReducer(gWithMomentum, useGraphCalculator=useGraphCalculator)
            break
        if graphReducer is None:
            raise CannotBeCalculatedError(graph)
    result = graphReducer.calculate()
    if not result:
        if suppressException:
            return None
        else:
            raise CannotBeCalculatedError(graph)
    evaluated = symbolic_functions.evaluate(result[0], result[1])
    return evaluated, graphReducer.iterationGraphs[0]


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
