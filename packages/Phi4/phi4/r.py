#!/usr/bin/python
# -*- coding: utf8
import itertools
import graphine.filters
import common

__author__ = 'daddy-bear'

import rggraphutil.symbolic_functions as symbolic_functions
import graphine.phi4
import gfun_calculator
import rggraphenv.storage as storage



@graphine.filters.graphFilter
def _is1Uniting(edgesList, superGraph, superGraphEdges):
    sg = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
    return len(sg.edges(sg.externalVertex)) == 2


def KRStar(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True):
    krs = KR1(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator, force=True, insideKRStar=True).subs(
        symbolic_functions.p, 1)
    spinneysGenerators = graphine.Graph.batchInitEdgesColors(
        [x for x in graph.xRelevantSubGraphs(filters=graphine.filters.oneIrreducible
                                                     + graphine.filters.isRelevant(graphine.phi4.UVRelevanceCondition())
                                                     + _is1Uniting,
                                             cutEdgesToExternal=False)])
    for i in xrange(1, len(spinneysGenerators) + 1):
        for spinney in itertools.combinations(spinneysGenerators, i):
            if not graphine.util.hasIntersectingByVertexesGraphs(spinney):
                spinneyPart = reduce(
                    lambda e, g: e * R(g, kOperation, uvSubGraphFilter,
                                       useGraphCalculator=useGraphCalculator,
                                       force=True),
                    spinney, 1)
                shrunk, p2Counts = shrinkToPoint(graph, spinney)
                ir = _irCOperation(shrunk, kOperation, uvSubGraphFilter, description, useGraphCalculator)
                krs += kOperation.calculate(spinneyPart * ir).subs(
                    symbolic_functions.p, 1)
    return krs


def _irCOperation(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True):
    body = _deleteExternalEdges(graph)
    kr1 = None
    for g in graphine.momentum.xArbitrarilyPassMomentum(body):
        try:
            if common.defaultGraphHasNotIRDivergence(g):
                kr1 = KR1(g, kOperation, uvSubGraphFilter,
                            description=description,
                            useGraphCalculator=useGraphCalculator,
                            force=True)
                break
            else:
                kr1 = KRStar(graph,
                             kOperation,
                             uvSubGraphFilter=uvSubGraphFilter,
                             description=description,
                             useGraphCalculator=useGraphCalculator)
        except common.CannotBeCalculatedError:
            pass
    if kr1 is None:
        raise common.CannotBeCalculatedError()
    return kr1 - _doIRSubtractingOperation(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator)


def _deleteExternalEdges(graph):
    return graph.deleteEdges(graph.edges(graph.externalVertex))


def _doIRSubtractingOperation(rawGraph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True):
    if len(rawGraph.edges(rawGraph.externalVertex)) == 2:
        iterator = [rawGraph]
    else:
        iterator = graphine.momentum.xPassExternalMomentum(rawGraph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        uvSubgraphs = graphine.Graph.batchInitEdgesColors([sg for sg in graph.xRelevantSubGraphs(uvSubGraphFilter)])
        sub = 0
        sign = 1
        for i in xrange(1, len(uvSubgraphs) + 1):
            sign *= -1
            for comb in itertools.combinations(uvSubgraphs, i):
                if not graphine.util.hasIntersectingByVertexesGraphs(comb):
                    r1 = reduce(lambda e, g: e * KR1(g, kOperation, uvSubGraphFilter, description=description,useGraphCalculator=useGraphCalculator, force=True), comb, 1)
                    if r1 != 0:
                        shrunk, p2Counts = shrinkToPoint(graph, comb)
                        ir = _irCOperation(shrunk, kOperation, uvSubGraphFilter, description, useGraphCalculator)
                        sub += sign * r1 * ir * (symbolic_functions.p2 ** p2Counts)
        return sub
    raise common.CannotBeCalculatedError(rawGraph)


def KR1(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True, force=False, insideKRStar=False):
    return _doKR1(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator, force, insideKRStar=insideKRStar)[0]


def _doKR1(rawGraph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True, force=False, insideKRStar=False):
    if len(rawGraph.edges(rawGraph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(rawGraph):
            raise AssertionError(str(rawGraph) + " - IR divergence")
        iterator = [rawGraph]
    else:
        iterator = graphine.momentum.xPassExternalMomentum(rawGraph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        evaluated = storage.getKR1(graph)
        if evaluated is not None and len(evaluated):
            for e in evaluated:
                return e[0], graph
        r1 = _doR1(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator, force=force)
        kr1 = kOperation.calculate(r1[0])
        storage.putGraphKR1(r1[1], kr1, common.GFUN_METHOD_NAME_MARKER, description)
        return kr1, graph

    if force:
        preferable, notPreferable = graphine.momentum.arbitrarilyPassMomentumWithPreferable(rawGraph, common.defaultGraphHasNotIRDivergence)
        for g in preferable:
            evaluated = storage.getKR1(g)
            if evaluated is not None and len(evaluated):
                for e in evaluated:
                    return e[0], rawGraph
            try:
                kr1 = KR1(g, kOperation, uvSubGraphFilter, description=description, useGraphCalculator=useGraphCalculator, force=force)
            except common.CannotBeCalculatedError:
                pass
            else:
                storage.putGraphKR1(g, kr1, common.GFUN_METHOD_NAME_MARKER, description)
                return kr1, g
        if not insideKRStar:
            for g in notPreferable:
                if g == rawGraph:
                    continue
                evaluated = storage.getKR1(g)
                if evaluated is not None and len(evaluated):
                    for e in evaluated:
                        return e[0], rawGraph
                try:
                    kr1 = KRStar(g, kOperation, uvSubGraphFilter, description=description, useGraphCalculator=useGraphCalculator)
                except common.CannotBeCalculatedError:
                    pass
                else:
                    storage.putGraphKR1(g, kr1, common.GFUN_METHOD_NAME_MARKER, description)
                    return kr1, g
    raise common.CannotBeCalculatedError(rawGraph)


def R(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True, force=False):
    """
    R = (1-K)R'
    """
    return _doR(graph, kOperation, uvSubGraphFilter, description=description, useGraphCalculator=useGraphCalculator, force=force)[0]


def _doR(rawGraph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True, force=False):
    if len(rawGraph.edges(rawGraph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(rawGraph):
            raise AssertionError(str(rawGraph) + " - IR divergence")
        iterator = [rawGraph]
    else:
        iterator = graphine.momentum.xPassExternalMomentum(rawGraph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        evaluated = storage.getR(graph)
        if evaluated is not None and len(evaluated):
            for e in evaluated:
                return e[0], graph
        r1 = _doR1(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator, force)[0]
        kr1 = _doKR1(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator, force)[0]
        r = r1 - kr1
        storage.putGraphR(graph, r, common.GFUN_METHOD_NAME_MARKER, description)
        return r, graph
    raise common.CannotBeCalculatedError(rawGraph)


def R1(graph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True, force=False):
    return _doR1(graph, kOperation, uvSubGraphFilter, description, useGraphCalculator, force)[0]


def _doR1(rawGraph, kOperation, uvSubGraphFilter, description="", useGraphCalculator=True, force=False):
    if len(rawGraph.edges(rawGraph.externalVertex)) == 2:
        if not force and not common.defaultGraphHasNotIRDivergence(rawGraph):
            raise AssertionError(str(rawGraph) + " - IR divergence")
        iterator = [rawGraph]
    else:
        iterator = graphine.momentum.xPassExternalMomentum(rawGraph, common.defaultGraphHasNotIRDivergenceFilter)
    for graph in iterator:
        evaluated = storage.getR1(graph)
        if evaluated is not None:
            for e in evaluated:
                return e[0], graph

        uvSubgraphs = graphine.Graph.batchInitEdgesColors([sg for sg in graph.xRelevantSubGraphs(uvSubGraphFilter)])
        if not len(uvSubgraphs):
            expression, twoTailsGraph = gfun_calculator.calculateGraphValue(graph, useGraphCalculator=useGraphCalculator)
            storage.putGraphR1(twoTailsGraph, expression, common.GFUN_METHOD_NAME_MARKER, description)
            return expression, twoTailsGraph

        rawRPrime = gfun_calculator.calculateGraphValue(graph, useGraphCalculator=useGraphCalculator)[0]
        sign = 1
        for i in xrange(1, len(uvSubgraphs) + 1):
            sign *= -1
            for comb in itertools.combinations(uvSubgraphs, i):
                if i == 1 or not graphine.util.hasIntersectingByVertexesGraphs(comb):
                    r1 = reduce(lambda e, g: e * KR1(g, kOperation, uvSubGraphFilter, useGraphCalculator=useGraphCalculator, force=force), comb, 1)
                    shrunk, p2Counts = shrinkToPoint(graph, comb)
                    rawRPrime += sign * r1 * gfun_calculator.calculateGraphValue(shrunk, useGraphCalculator=useGraphCalculator)[0] * (symbolic_functions.p2 ** p2Counts)

        storage.putGraphR1(graph, rawRPrime, common.GFUN_METHOD_NAME_MARKER, description)
        return rawRPrime, graph
    raise common.CannotBeCalculatedError(rawGraph)


def shrinkToPoint(graph, subGraphs):
    toShrink = list()
    p2Counts = 0
    excludedEdges = set()
    for sg in subGraphs:
        edge = _hasMomentumQuadraticDivergence(sg, graph, excludedEdges)
        if edge is not None:
            toShrink.append(graphine.Graph([edge], graph.externalVertex, renumbering=False))
            p2Counts += 1
        toShrink.append(sg)
    shrunk = graph.batchShrinkToPoint(toShrink)
    return shrunk, p2Counts


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