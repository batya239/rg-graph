#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import graph_state
import graph_storage
import lambda_number
import momentum


def _createFilter():
    class Model:
    # noinspection PyUnusedLocal
        def isRelevant(self, edgesList, superGraph, superGraphEdges):
            subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
            vertexes = set()
            for e in subGraph.edges(superGraph.externalVertex):
                vertexes |= set(e.nodes)
                # external node and 2 internals
            return len(vertexes) == 3

    return graphine.filters.oneIrreducible + graphine.filters.noTadpoles + graphine.filters.isRelevant(Model())


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
    def __init__(self, graph, momentumPassing=list(), subGraphFilters=list()):
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
        self._subGraphFilter = _createFilter()

    @property
    def iterationValues(self):
        return self._iterationValues

    @property
    def iterationGraphs(self):
        return self._iterationGraphs

    def getCurrentIterationGraph(self):
        return self._iterationGraphs[-1]

    def getCurrentIterationValue(self):
        return self._iterationValues[-1] if len(self._iterationValues) else None

    def nextIteration(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        lastIteration = self.getCurrentIterationGraph()
        if len(lastIteration.allEdges()) == 3:
            self._putFinalValueToGraphStorage()
            return False

        if self._tryReduceChain():
            return True

        maximal = None
        for subGraphAsList in \
                    [x for x in lastIteration.xRelevantSubGraphs(self._subGraphFilter, graphine.Representator.asList)] \
                    + [lastIteration.allEdges()]:
            if not maximal or len(subGraphAsList) > len(maximal):
                adjustedSubGraph = _adjust(subGraphAsList, self._initGraph.externalVertex)
                subGraph = graphine.Graph(adjustedSubGraph[0],
                                          externalVertex=self._initGraph.externalVertex,
                                          renumbering=False)
                subGraphState = subGraph.toGraphState()
                if graph_storage.has(subGraphState):
                    maximal = (adjustedSubGraph[1], subGraphState, adjustedSubGraph[2])
        if not maximal:
            return False

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
                    newLambdaNumber = lambda_number.LambdaNumber.fromRainbow(e)
                else:
                    newLambdaNumber += lambda_number.LambdaNumber.fromRainbow(e)
                for currentVertex in e.nodes:
                    if currentVertex != v:
                        boundaryVertexes.append(currentVertex)
            assert newLambdaNumber
            newEdge = graph_state.Edge(boundaryVertexes,
                                       external_node=self._initGraph.externalVertex,
                                       colors=newLambdaNumber.toRainbow())
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
                    return copy.copy(edges), v
        return None

    def _putFinalValueToGraphStorage(self):
        gValue = "*".join(self._iterationValues)

        innerEdge = None
        for e in self.getCurrentIterationGraph().allEdges():
            if self._initGraph.externalVertex not in e.nodes:
                innerEdge = e
                break
        assert innerEdge

        wValue = innerEdge.colors

        graph_storage.put(self._initGraph.toGraphState(), (gValue, wValue))




