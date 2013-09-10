#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import graph_state
from rggraphutil.env import storage, graph_calculator
import common
import lambda_number
import symbolic_functions


def _createFilter():
    class RelevanceCondition:
    # noinspection PyUnusedLocal
        def __init__(self):
            pass

        def isRelevant(self, edgesList, superGraph, superGraphEdges):
            subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
            vertexes = set()
            for e in subGraph.edges(superGraph.externalVertex):
                vertexes |= set(e.nodes)
                # external node and 2 internals
            return len(vertexes) == 3

    #return graphine.filters.oneIrreducible + graphine.filters.noTadpoles + graphine.filters.isRelevant(
    return graphine.filters.oneIrreducible + graphine.filters.isRelevant(
        RelevanceCondition())


def calculateGraphsValues(graphs, suppressException=False, useGraphCalculator=False):
    return reduce(lambda e, g: e * calculateGraphValue(g, suppressException, useGraphCalculator=useGraphCalculator)[0], graphs, 1)


def calculateGraphValue0(graph, suppressException=False, useGraphCalculator=False):
    return calculateGraphValue(graph, suppressException, useGraphCalculator)[0]


def calculateGraphValue(graph, suppressException=False, useGraphCalculator=False):
    if len(graph.edges(graph.externalVertex)) == 2:
        graphReducer = GGraphReducer(graph, useGraphCalculator=useGraphCalculator)
    else:
        graphReducer = None
        for gWithMomentum in graphine.momentum.xPassExternalMomentum(graph, common.defaultGraphHasNotIRDivergenceFilter):
            graphReducer = GGraphReducer(gWithMomentum, useGraphCalculator=useGraphCalculator)
            break
        if graphReducer is None:
            raise common.CannotBeCalculatedError(graph)
    result = graphReducer.calculate()
    if not result:
        if suppressException:
            return None
        else:
            raise common.CannotBeCalculatedError(graph)
    evaluated = symbolic_functions.evaluate(result[0], result[1])
    return evaluated, graphReducer.iterationGraphs[0]


def _adjust(graphAsList, externalVertex):
    adjustedEdges = []
    boundaryVertexes = set()
    for e in graphAsList:
        if externalVertex in e.nodes:
            boundaryVertexes |= set(e.nodes)
        else:
            adjustedEdges.append(e)
    boundaryVertexes.remove(externalVertex)
    adjustedExternalEdges = []
    for v in boundaryVertexes:
        adjustedExternalEdges.append(graph_state.Edge((externalVertex, v), external_node=externalVertex, colors=(0, 0)))
    return adjustedEdges + adjustedExternalEdges, adjustedEdges, boundaryVertexes


class GGraphReducer(object):
    DEBUG = False

    @staticmethod
    def setDebug(debug):
        GGraphReducer.DEBUG = debug

    def __init__(self,
                 graph,
                 momentumPassing=list(),
                 subGraphFilters=list(),
                 rawFilters=False,
                 useGraphCalculator=False,
                 iterationGraphs=None,
                 iterationValues=None):
        """
        momentumPassing -- two external edges of graph in which external momentum passing
        """
        if isinstance(graph, graphine.Graph):
            if len(momentumPassing):
                self._initGraph = graphine.momentum.passMomentOnGraph(graph, momentumPassing)
            else:
                self._initGraph = graph
        else:
            raise TypeError('unsupported type of initial graph')
        self._iterationGraphs = [self._initGraph] if iterationGraphs is None else iterationGraphs
        self._iterationValues = [] if iterationValues is None else iterationValues
        self._subGraphFilter = subGraphFilters if rawFilters else (_createFilter() + subGraphFilters)
        self._useGraphCalculator = useGraphCalculator
        self._isTadpole = None

    @property
    def iterationValues(self):
        return self._iterationValues

    @property
    def iterationGraphs(self):
        return self._iterationGraphs

    @property
    def externalVertex(self):
        return self._initGraph.externalVertex

    @property
    def iterationsCount(self):
        return len(self._iterationValues)

    def getCurrentIterationGraph(self):
        return self._iterationGraphs[-1]

    def getCurrentIterationValue(self):
        return self._iterationValues[-1] if len(self._iterationValues) else None

    def isSuccesfulDone(self):
        return len(self.getCurrentIterationGraph().allEdges()) == 3

    def calculate(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        lastIteration = self.getCurrentIterationGraph()
        if self._isTadpole is None:
            self._isTadpole = str(lastIteration).startswith("ee")
            if self._isTadpole:
                return "0", (0, 0)

        if len(lastIteration.allEdges()) == 3 or str(lastIteration).startswith("ee"):
            self._putFinalValueToGraphStorage()
            if GGraphReducer.DEBUG:
                print self._iterationGraphs
                print self._iterationValues
            return self.getFinalValue()

        relevantSubGraphs = [x for x in
                             lastIteration.xRelevantSubGraphs(self._subGraphFilter, graphine.Representator.asList)] + [
                             lastIteration.allEdges()]
        relevantSubGraphs = relevantSubGraphs[::-1]
        relevantSubGraphs.sort(lambda x, y: len(y) - len(x))

        for subGraphAsList in relevantSubGraphs:
            adjustedSubGraph = _adjust(subGraphAsList, self._initGraph.externalVertex)
            subGraph = graphine.Graph(adjustedSubGraph[0], externalVertex=self._initGraph.externalVertex)
            preprocessed = (adjustedSubGraph[1], subGraph, adjustedSubGraph[2])
            if storage.hasGraph(subGraph):
                res = self._doIterate(preprocessed)
                if res is not None:
                    return res
                continue
            if self._useGraphCalculator:
                result = graph_calculator.tryCalculate(subGraph, putValueToStorage=True)
                if result is not None:
                    res = self._doIterate(preprocessed)
                    if res is not None:
                        return res

        return self._tryReduceChain2()

    def _doIterate(self, subGraphInfo):
        assert len(subGraphInfo[2]) == 2
        newIteration = self.getCurrentIterationGraph().deleteEdges(subGraphInfo[0])

        maximalSubGraphValue = storage.getGraph(subGraphInfo[1])

        newIteration = newIteration.addEdge(graph_state.Edge(subGraphInfo[2], self._initGraph.externalVertex,
                                                             colors=maximalSubGraphValue[0][1]))

        newIterationGraphs = copy.copy(self._iterationGraphs)
        newIterationGraphs.append(newIteration)
        newIterationValues = copy.copy(self._iterationValues)
        newIterationValues.append(maximalSubGraphValue[0][0])

        newReducer = GGraphReducer(self._initGraph,
                                   useGraphCalculator=self._useGraphCalculator,
                                   rawFilters=True,
                                   subGraphFilters=self._subGraphFilter,
                                   iterationGraphs=newIterationGraphs,
                                   iterationValues=newIterationValues)

        return newReducer.calculate()

    def nextIteration(self):
        """
        now this is deprecated!!!

        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        lastIteration = self.getCurrentIterationGraph()
        if len(lastIteration.allEdges()) == 3:
            self._putFinalValueToGraphStorage()
            return False

        if storage.hasGraph(lastIteration):
            v = storage.getGraph(lastIteration)
            edge1 = graph_state.Edge(nodes=(self.externalVertex, 0))
            edge2 = graph_state.Edge(nodes=(self.externalVertex, 1))
            edge3 = graph_state.Edge(nodes=(0, 1), colors=v[0][1])
            self._iterationGraphs.append(graphine.Graph([edge1, edge2, edge3]))
            self._iterationValues.append(v[0][0])
            return True

        maximal = None
        relevantSubGraphs = [x for x in
                             lastIteration.xRelevantSubGraphs(self._subGraphFilter, graphine.Representator.asList)]
        relevantSubGraphs = relevantSubGraphs[::-1]

        for subGraphAsList in relevantSubGraphs:
            if not maximal or len(subGraphAsList) > len(maximal[1].allEdges()):
                adjustedSubGraph = _adjust(subGraphAsList, self._initGraph.externalVertex)
                subGraph = graphine.Graph(adjustedSubGraph[0], externalVertex=self._initGraph.externalVertex)
                if GGraphReducer.DEBUG:
                    print "relevant subgraph:", subGraph
                preprocessed = (adjustedSubGraph[1], subGraph, adjustedSubGraph[2])
                if storage.hasGraph(subGraph):
                    maximal = preprocessed
                    break
                if self._useGraphCalculator:
                    result = graph_calculator.tryCalculate(subGraph, putValueToStorage=True)
                    if result is not None:
                        maximal = preprocessed
                        break

        if not maximal:
            if maximal is None:
                return self._tryReduceChain()

        assert len(maximal[2]) == 2
        newIteration = lastIteration.deleteEdges(maximal[0])

        maximalSubGraphValue = storage.getGraph(maximal[1])

        newIteration = newIteration.addEdge(graph_state.Edge(maximal[2], self._initGraph.externalVertex,
                                                             colors=maximalSubGraphValue[0][1]))

        self._iterationGraphs.append(newIteration)
        self._iterationValues.append(maximalSubGraphValue[0][0])

        return True

    def _tryReduceChain2(self):
        edgesAndVertex = self._searchForChains()
        if not edgesAndVertex:
            return None
        else:
            edges, v = edgesAndVertex
            assert len(edges) == 2
            boundaryVertexes = []
            newLambdaNumber = None
            for e in edges:
                if not newLambdaNumber:
                    newLambdaNumber = lambda_number.fromRainbow(e)
                else:
                    newLambdaNumber += lambda_number.fromRainbow(e)
                for currentVertex in e.nodes:
                    if currentVertex != v:
                        boundaryVertexes.append(currentVertex)
            assert newLambdaNumber
            newEdge = graph_state.Edge(boundaryVertexes,
                                       external_node=self._initGraph.externalVertex,
                                       colors=lambda_number.toRainbow(newLambdaNumber))
            currentGraph = self.getCurrentIterationGraph()
            currentGraph = currentGraph.deleteEdges(edges)
            currentGraph = currentGraph.addEdge(newEdge)
            self._iterationGraphs.append(currentGraph)
            return self.calculate()

    def _tryReduceChain(self):
        edgesAndVertex = self._searchForChains()
        if not edgesAndVertex:
            return False
        else:
            edges, v = edgesAndVertex
            assert len(edges) == 2
            boundaryVertexes = []
            newLambdaNumber = None
            for e in edges:
                if not newLambdaNumber:
                    newLambdaNumber = lambda_number.fromRainbow(e)
                else:
                    newLambdaNumber += lambda_number.fromRainbow(e)
                for currentVertex in e.nodes:
                    if currentVertex != v:
                        boundaryVertexes.append(currentVertex)
            assert newLambdaNumber
            newEdge = graph_state.Edge(boundaryVertexes,
                                       external_node=self._initGraph.externalVertex,
                                       colors=lambda_number.toRainbow(newLambdaNumber))
            currentGraph = self.getCurrentIterationGraph()
            currentGraph = currentGraph.deleteEdges(edges)
            currentGraph = currentGraph.addEdge(newEdge)
            self._iterationGraphs.append(currentGraph)
            return True

    def _searchForChains(self):
        currentGraph = self.getCurrentIterationGraph()
        for v in currentGraph.vertexes():
            if v is not currentGraph.externalVertex:
                edges = currentGraph.edges(v)
                if len(edges) == 2:
                    #checks no external edge
                    if currentGraph.externalVertex in edges[0].nodes or currentGraph.externalVertex in edges[1].nodes:
                        continue
                    return copy.copy(edges), v
        return None

    def getFinalValue(self):
        assert self.isSuccesfulDone()
        if str(self.getCurrentIterationGraph()).startswith("ee"):
            return "0", (0, 0)
        gValue = "*".join(map(lambda v: v if v[0] == 'G' else "(%s)" % v, self._iterationValues))
        innerEdge = None
        for e in self._iterationGraphs[-1].allEdges():
            if self._initGraph.externalVertex not in e.nodes:
                innerEdge = e
                break
        assert innerEdge

        wValue = innerEdge.colors

        return gValue, wValue

    def _putFinalValueToGraphStorage(self):
        storage.putGraph(self._initGraph, self.getFinalValue(), common.GFUN_METHOD_NAME_MARKER)