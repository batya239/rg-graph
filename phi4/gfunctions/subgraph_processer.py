#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import itertools
import graph_state
import graph_storage
import lambda_number


def xPickPassingExternalMomentum(graph):
    """
    find all cases for passing external momentum
    """
    externalEdges = graph.edges(graph.externalVertex)
    for edgesPair in itertools.combinations(externalEdges, 2):
        vertexes = set()
        for e in edgesPair:
            vertexes |= set(e.nodes)
        if len(vertexes) == 3:
            yield edgesPair


def _createFilter():
    class Model:
    # noinspection PyUnusedLocal
        def isRelevant(self, edgesList, superGraph, superGraphEdges):
            subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
            vertexes = set()
            for e in subGraph.edges(superGraph.externalVertex):
                vertexes |= set(e.nodes)
            return len(vertexes) == 3 # external node and 2 internals

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
    def __init__(self, graph, momentumPassing):
        """
        momentumPassing -- two external edges of graph in which external momentum passing
        """
        if isinstance(graph, graphine.Graph):
            edgesToRemove = list()
            copiedMomentumPassing = list(momentumPassing)
            for e in graph.edges(graph.externalVertex):
                if e in copiedMomentumPassing:
                    copiedMomentumPassing.remove(e)
                else:
                    edgesToRemove.append(e)
            self._initGraph = graph.deleteEdges(edgesToRemove)
        else:
            raise TypeError('unsupported type of initial graph')
        self.iterationsGraph = [self._initGraph]
        self.iterationsValue = []
        self.subGraphFilter = _createFilter()

    def nextIteration(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        if self._tryReduceChain():
            return True

        lastIteration = self.getCurrentIterationGraph()
        maximal = None
        for subGraphAsList in [lastIteration.allEdges()] \
                + [x for x in lastIteration.xRelevantSubGraphs(self.subGraphFilter, graphine.Representator.asList)]:
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

        newIteration.addEdge(graph_state.Edge(maximal[2], self._initGraph.externalVertex,
                                              colors=maximalSubGraphValue[1]))

        self.iterationsGraph.append(newIteration)
        self.iterationsValue.append(maximalSubGraphValue[0])

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
                                       colors=newLambdaNumber.asRainbow())
            currentGraph = self.getCurrentIterationGraph()
            currentGraph = currentGraph.deleteEdges(edges)
            currentGraph = currentGraph.addEdge(newEdge)
            self.iterationsGraph.append(currentGraph)
            return True

    def _searchForChains(self):
        currentGraph = self.getCurrentIterationGraph()
        for v in currentGraph.vertexes():
            if v is not currentGraph.externalVertex:
                edges = currentGraph.edges(v)
                if len(edges) == 2:
                    return copy.copy(edges), v
        return None

    def getCurrentIterationGraph(self):
        return self.iterationsGraph[-1]

    def getCurrentIterationValue(self):
        return self.iterationsValue[-1] if len(self.iterationsValue) else None



