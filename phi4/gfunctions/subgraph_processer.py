#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import itertools


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
    pass


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
        find maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        lastIteration = self.getCurrentIteration()
        maximal = None
        for subGraphAsList in lastIteration.xRelevantSubGraphs(self.subGraphFilter, graphine.Representator.asList):
            if not maximal or len(subGraphAsList) > len(maximal):
                subGraph = graphine.Graph(subGraphAsList,
                                          externalVertex=self._initGraph.externalVertex,
                                          renumbering=False)
                subGraphState = subGraph.toGraphState()
                if self.graphStorage.has(subGraphState):
                    maximal = (subGraphAsList, subGraph, subGraphState)
        if not maximal:
            return False

    def searchForChains(self):
        externalEdges = self._initGraph.edges(self._initGraph.externalVertex)

    def getCurrentIteration(self):
        return self.iterations[-1] if len(self.iterations) else (self._initGraph, None)

    def getAllIterations(self):
        return self.iterations