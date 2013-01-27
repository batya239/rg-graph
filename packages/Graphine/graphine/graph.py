#!/usr/bin/python
# -*- coding: utf8
import copy
from graph_state import graph_state


class RelevantGraphsAware(object):
    def isRelevant(self, graph):
        pass


class Graph(object):
    """
    representation of graph
    """

    def __init__(self, obj):
        """
        self.edges - dict where keys is one vertex of edge and value is list of second vertexes
        """
        if isinstance(obj, list):
            self._edges = Graph._parseEdges(graph_state.GraphState(obj).edges)
        elif isinstance(obj, dict):
            self._edges = obj
        elif isinstance(obj, graph_state.GraphState):
            self._edges = Graph._parseEdges(obj.edges)
        self._nextVertexIndex = max(self._edges.keys()) + 1

    def vertexes(self):
        return set(self._edges.keys())

    def createVertexIndex(self):
        toReturn = self._nextVertexIndex
        self._nextVertexIndex += 1
        return toReturn

    def edges(self, vertex):
        return self._edges.get(vertex, [])

    def allEdges(self):
        edgesOccurrence = dict()
        for edges in self._edges.values():
            for edge in edges:
                v1, v2 = edge.nodes
                occurrenceRate = 2 if v1 == v2 else 1
                if edge in edgesOccurrence:
                    edgesOccurrence[edge] += occurrenceRate
                else:
                    edgesOccurrence[edge] = occurrenceRate
        result = []
        for e, o in edgesOccurrence.items():
            for i in xrange(0, o / 2):
                result.append(e)
        return result

    def change(self, oldEdges, newEdges):
        for e in oldEdges:
            self.deleteEdge(e)
        for e in newEdges:
            self.addEdge(e)

    def addEdge(self, edge):
        """
        immutable operation
        """
        v1, v2 = edge.nodes
        newEdges = copy.copy(self._edges)
        for v in set([v1, v2]):
            Graph._insertEdge(newEdges, v, edge)
        return Graph(newEdges)

    def deleteEdge(self, edge):
        """
        immutable operation
        """
        v1, v2 = edge.nodes
        newEdges = copy.copy(self._edges)
        for v in set([v1, v2]):
            Graph._deleteEdge(newEdges, v, edge)
        return Graph(newEdges)

    def shrinkToPoint(self, edges):
        """
        obj -- list of edges or graph
        immutable operation
        """
        newRawEdges = copy.copy(self.allEdges())
        markedVertexes = set()
        for edge in edges:
            v1, v2 = edge.nodes
            newRawEdges.remove(edge)
            markedVertexes.add(v1)
            markedVertexes.add(v2)

        newEdges = []
        for edge in newRawEdges:
            v1, v2 = edge.nodes
            copyMap = {}
            if v1 in markedVertexes:
                copyMap[v1] = self._nextVertexIndex
            if v2 in markedVertexes:
                copyMap[v2] = self._nextVertexIndex
            if len(copyMap):
                newEdges.append(edge.copy(copyMap))
            else:
                newEdges.append(edge)

        return Graph(newEdges)

    def findRelevantSubGraphs(self, relevantGraphsAwareObj, checkFor1Irreducible):
        pass

    def find1IrreducibleSubGraphs(self):
        pass

    def toGraphState(self):
        return graph_state.GraphState(self.allEdges())

    @staticmethod
    def _parseEdges(edgesIterable):
        edgesDict = dict()
        for edge in edgesIterable:
            v1, v2 = edge.nodes
            Graph._insertEdge(edgesDict, v1, edge)
            if v1 != v2:
                Graph._insertEdge(edgesDict, v2, edge)
        return edgesDict

    @staticmethod
    def _insertEdge(edgesDict, vertex, edge):
        if vertex in edgesDict:
            edgesDict[vertex].append(edge)
        else:
            edgesDict[vertex] = [edge]

    @staticmethod
    def _deleteEdge(edgesDict, vertex, edge):
        try:
            edgesDict[vertex].remove(edge)
        except KeyError as e:
            raise ValueError(e), "edge not exists in graph"
