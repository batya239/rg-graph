#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import itertools
import graph_state
from phi4.gfunctions import lambda_number


def xPickPassingExternalMomentum(graph):
    """
    find all cases for passing external momentum
    """
    externalEdges = graph.edges(graph.externalVertex)
    for edgesPair in itertools.combinations(externalEdges, 2):
        vertexes = set()
        for e in edgesPair:
            vertexes += dict(e.nodes)
        if len(vertexes) == 3:
            yield edgesPair


def createFilter():
    class Model:
    # noinspection PyUnusedLocal
        def isRelevant(self, edgesList, superGraph, superGraphEdges):
            subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
            vertexes = set()
            for e in subGraph.edges(superGraph.externalVertex):
                vertexes += set(e.nodes)
            return len(vertexes) == 3

    return graphine.filters.oneIrreducible + graphine.filters.noTadpoles + graphine.filters.isRelevant(Model())


class Step(object):
    def __init__(self, isLineReducing, graph, obj):
        self.isLineReducing = isLineReducing
        self.graph = graph
        self.obj = obj

    @staticmethod
    def lineReducing(graph, lines):
        return Step(True, graph, tuple(lines))

    @staticmethod
    def graphReducing(graph, subGraph):
        return Step(False, graph, subGraph)


class GGraphReducer(object):
    def __init__(self, graph, momentumPassing, graphStorage):
        """
        momentumPassing -- two external edges of graph in which external momentum passing
        """
        if isinstance(graph, graphine.Graph):
            edgesToRemove = list()
            copiedMomentumPassing = copy.copy(momentumPassing)
            for e in graph.edges(graph.externalVertex):
                if e in copiedMomentumPassing:
                    copiedMomentumPassing.remove(e)
                else:
                    edgesToRemove.append(e)
            self._initGraph = graph.deleteEdges(edgesToRemove)
        else:
            raise TypeError('unsupported type of initial graph')
        self.iterations = []
        self.graphStorage = graphStorage
        self.subGraphFilter = createFilter()

    def nextIteration(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        if self.tryReduceChain():
            return True

        lastIteration = self.getCurrentIterationGraph()
        maximal = None
        for subGraphAsList in lastIteration.xRelevantSubGraphs(self.subGraphFilter, graphine.Representator.asList):
            if not maximal or len(subGraphAsList) > len(maximal):
                subGraph = graphine.Graph(subGraphAsList,
                                          externalVertex=self._initGraph.externalVertex,
                                          renumbering=False)
                subGraphState = subGraph.toGraphState()
                if self.graphStorage.has(subGraphState):
                    maximal = (subGraphAsList, subGraphState)
        if not maximal:
            return False

        subExternalVertexes = graphine.util.getSubExternalVertexes(lastIteration, maximal[1])
        assert len(subExternalVertexes) == 2
        newIteration = lastIteration.deleteEdges(maximal[1])
        #TODO
        newIteration.addEdge(graph_state.Edge(subExternalVertexes))

    def tryReduceChain(self):
        edgesAndVertex = self.searchForChains()
        if not edgesAndVertex:
            return False
        else:
            edges, v = edgesAndVertex
            assert len(edges) == 2
            boundaryVertexes = []
            newLambdaNumber = None
            for e in edges:
                if not newLambdaNumber:
                    newLambdaNumber = lambda_number.LambdaNumber.fromRainbow(e.colors)
                else:
                    newLambdaNumber += lambda_number.LambdaNumber.fromRainbow(e.colors)
                for currentVertex in e.nodes:
                    if currentVertex != v:
                        boundaryVertexes.append(currentVertex)
            assert newLambdaNumber
            newEdge = graph_state.Edge(boundaryVertexes,
                                       external_node=self._initGraph.externalVertex,
                                       colors=newLambdaNumber.toRainbow())
            currentGraph = self.getCurrentIteration()
            currentGraph = currentGraph.deleteEdges(edges)
            currentGraph = currentGraph.addEdge(newEdge)
            self.iterations.append(Step.lineReducing(currentGraph, edges))

    def searchForChains(self):
        currentGraph = self.getCurrentIterationGraph()
        for v in currentGraph.vertexes():
            edges = currentGraph.edges(v)
            if len(edges) == 2:
                return edges, v
        return None

    def getCurrentIterationGraph(self):
        if not len(self.iterations):
            return self._initGraph
        else:
            return self.iterations[-1].graph

    def getCurrentIteration(self):
        return self.iterations[-1] if len(self.iterations) else (self._initGraph, None)

    def getAllIterations(self):
        return self.iterations
