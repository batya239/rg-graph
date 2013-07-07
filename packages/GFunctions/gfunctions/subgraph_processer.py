#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import graph_state
import graph_calculator
import graph_storage
import lambda_number
import momentum
import symbolic_functions


def _createFilter():
    class RelevanceCondition:
    # noinspection PyUnusedLocal
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
    def __init__(self, graph, momentumPassing=list(), subGraphFilters=list(), useGraphCalculator=False):
        """
        momentumPassing -- two external edges of graph in which external momentum passing
        """
        if isinstance(graph, graphine.Graph):
            if len(momentumPassing):
                self._initGraph = momentum.passMomentOnGraph(graph, momentumPassing)
            else:
                self._initGraph = graph
        else:
            raise TypeError('unsupported type of initial graph')
        self._iterationGraphs = [self._initGraph]
        self._iterationValues = []
        self._subGraphFilter = _createFilter() + subGraphFilters
        self._useGraphCalculator = useGraphCalculator

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

    def nextIteration(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        lastIteration = self.getCurrentIterationGraph()
        if len(lastIteration.allEdges()) == 3:
            self._putFinalValueToGraphStorage()
            return False

        maximal = None
        relevantSubGraphs = [x for x in lastIteration.xRelevantSubGraphs(self._subGraphFilter, graphine.Representator.asList)] + [
            lastIteration.allEdges()]

        preProcessedSubGraphs = list()
        for subGraphAsList in relevantSubGraphs:
            if not maximal or len(subGraphAsList) > len(maximal[1].allEdges()):
                adjustedSubGraph = _adjust(subGraphAsList, self._initGraph.externalVertex)
                subGraph = graphine.Graph(adjustedSubGraph[0], externalVertex=self._initGraph.externalVertex)
                preprocessed = (adjustedSubGraph[1], subGraph, adjustedSubGraph[2])
                if graph_storage.has(subGraph):
                    preProcessedSubGraphs = None
                    maximal = preprocessed
                elif preProcessedSubGraphs is not None:
                    preProcessedSubGraphs.append(preprocessed)

        if not maximal:
            if self._useGraphCalculator:
                for preprocessed in preProcessedSubGraphs:
                    subGraph = preprocessed[1]
                    result = graph_calculator.tryCalculate(subGraph)
                    if result is not None:
                        graph_storage.put(subGraph, (symbolic_functions.toExternalCode(str(result[0])), (0, 0)))
                        maximal = preprocessed
                        break
            if maximal is None:
                return self._tryReduceChain()

        assert len(maximal[2]) == 2
        newIteration = lastIteration.deleteEdges(maximal[0])

        maximalSubGraphValue = graph_storage.get(maximal[1])

        newIteration = newIteration.addEdge(graph_state.Edge(maximal[2], self._initGraph.externalVertex,
                                                             colors=maximalSubGraphValue[1]))

        self._iterationGraphs.append(newIteration)
        self._iterationValues.append(maximalSubGraphValue[0])

        return True

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
        graph_storage.put(self._initGraph, self.getFinalValue())


class TwoChoicesStrategy(object):




