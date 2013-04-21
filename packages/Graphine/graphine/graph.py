#!/usr/bin/python
# -*- coding: utf8
import copy
from graph_state import graph_state, Edge
import graph_operations


class Representator:
    def __init__(self):
        raise AssertionError

    # noinspection PyUnusedLocal
    @staticmethod
    def asList(edgeList, externalVertex):
        return edgeList

    @staticmethod
    def asGraph(edgeList, externalVertex):
        return Graph(edgeList, externalVertex=externalVertex, renumbering=False)

    @staticmethod
    def asMinimalGraph(edgeList, externalVertex):
        return Graph(edgeList, externalVertex=externalVertex, renumbering=True)


class IndexableEdge:
    def __init__(self, underlyingEdge, index):
        self._underlyingEdge = underlyingEdge
        self._index = index

    @property
    def underlying(self):
        return self._underlyingEdge

    @property
    def index(self):
        return self._index

    def __eq__(self, other):
        return other.index - self.index == 0 and self.underlying == other.underlying

    def __hash__(self):
        return hash(self.index) * 37 + hash(self.underlying)

    @staticmethod
    def toIndexless(obj):
        """
        return graph_state.Edge's
        """
        if isinstance(obj, IndexableEdge):
            return obj.underlying
        else:
            return map(lambda ie: ie.underlying, obj)


class Graph(object):
    """
    representation of graph
    """

    def __init__(self, obj, externalVertex=-1, renumbering=True):
        """
        self.edges - dict where keys is one vertex of edge and value is list of second vertexes
        """
        if isinstance(obj, list):
            self._edges = Graph._parseEdges(graph_state.GraphState(obj).edges if renumbering else obj)
        elif isinstance(obj, dict):
            self._edges = obj
        elif isinstance(obj, graph_state.GraphState):
            self._edges = Graph._parseEdges(obj.edges)
        self._nextVertexIndex = max(self._edges.keys()) + 1
        self._externalVertex = externalVertex

    @property
    def externalVertex(self):
        return self._externalVertex

    def vertexes(self):
        return set(self._edges.keys())

    def createVertexIndex(self):
        toReturn = self._nextVertexIndex
        self._nextVertexIndex += 1
        return toReturn

    def edges(self, vertex, withIndex=False):
        vertexEdges = copy.copy(self._edges.get(vertex, []))
        return vertexEdges if withIndex else IndexableEdge.toIndexless(vertexEdges)

    def allEdges(self, withIndex=False):
        edgesOccurrence = dict()
        for edges in self._edges.values():
            for edge in edges:
                v1, v2 = edge.underlying.nodes
                occurrenceRate = 2 if v1 == v2 else 1
                if edge in edgesOccurrence:
                    edgesOccurrence[edge] += occurrenceRate
                else:
                    edgesOccurrence[edge] = occurrenceRate
        result = []
        for e, o in edgesOccurrence.items():
            for i in xrange(0, o / 2):
                result.append(e)
        return result if withIndex else IndexableEdge.toIndexless(result)

    def change(self, oldEdges, newEdges):
        for e in oldEdges:
            self.deleteEdge(e)
        for e in newEdges:
            self.addEdge(e)

    def addEdges(self, edgesToAdd):
        """
        immutable operation
        """
        newEdges = self.allEdges() + edgesToAdd
        return Graph(newEdges)

    def addEdge(self, edge):
        return self.addEdges([edge])

    def deleteEdges(self, edgesToRemove):
        """
        immutable operation
        """
        newEdges = copy.deepcopy(self._edges)
        for edge in edgesToRemove:
            Graph._persDeleteEdge(newEdges, edge)
        return Graph(newEdges)

    def deleteVertex(self, vertex):
        assert vertex != self.externalVertex
        return self.deleteEdges(self.edges(vertex))

    def deleteEdge(self, edge):
        return self.deleteEdges([edge])

    def identifyVertexes(self, vertexesToIdentify):
        pass

    def hasTadpoles(self):
        for edge in self.allEdges():
            if len(set(edge.nodes)) == 1:
                return True
        return False

    def batchShrinkToPoint(self, subGraphs):
        """
        subGraphs -- list of graphs edges
        """
        if not len(subGraphs):
            return self

        vertexTransformation = ID_VERTEX_TRANSFORMATION
        g = self
        for subGraph in subGraphs:
            g, vertexTransformation = g._shrinkToPoint(subGraph, vertexTransformation)
        assert g
        return g

    def _shrinkToPoint(self, unTransformedEdges, vertexTransformation=None):
        """
        obj -- list of edges or graph
        immutable operation
        """
        if not vertexTransformation:
            vertexTransformation = ID_VERTEX_TRANSFORMATION

        edges = map(lambda e: e.copy(vertexTransformation.mapping), unTransformedEdges)

        newRawEdges = copy.copy(self.allEdges())
        markedVertexes = set()
        for edge in edges:
            v1, v2 = edge.nodes
            newRawEdges.remove(edge)
            markedVertexes.add(v1)
            markedVertexes.add(v2)

        newEdges = []
        currVertexTransformationMap = dict()
        for edge in newRawEdges:
            v1, v2 = edge.nodes
            copyMap = {}
            if v1 in markedVertexes:
                currVertexTransformationMap[v1] = self._nextVertexIndex
                copyMap[v1] = self._nextVertexIndex
            if v2 in markedVertexes:
                currVertexTransformationMap[v2] = self._nextVertexIndex
                copyMap[v2] = self._nextVertexIndex
            if len(copyMap):
                newEdges.append(edge.copy(copyMap))
            else:
                newEdges.append(edge)
        return Graph(newEdges, externalVertex=self.externalVertex, renumbering=False), \
               vertexTransformation.add(VertexTransformation(currVertexTransformationMap))

    def shrinkToPoint(self, edges):
        return self._shrinkToPoint(edges)[0]

    def xRelevantSubGraphs(self, filters=list(), resultRepresentator=Representator.asGraph):
        allEdges = self.allEdges()
        simpleCache = dict()
        for subGraphAsList in graph_operations._xSubGraphs(allEdges, self.externalVertex):
            subGraphAsTuple = tuple(subGraphAsList)
            isValid = simpleCache.get(subGraphAsTuple, None)
            if isValid is None:
                isValid = True
                for aFilter in filters:
                    if not aFilter(subGraphAsList, self, allEdges):
                        isValid = False
                        break
            if isValid:
                yield resultRepresentator(subGraphAsList, self.externalVertex)

    def toGraphState(self):
        return graph_state.GraphState(self.allEdges())

    def calculateLoopsCount(self):
        return len(self.allEdges()) - len(self.edges(self.externalVertex)) - (len(self.vertexes()) - 1) + 1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.toGraphState())

    @staticmethod
    def initEdgesColors(graph, zeroColor=(0, 0), unitColor=(1, 0)):
        edges = graph.allEdges()
        initedEdges = list()
        for e in edges:
            color = zeroColor if graph.externalVertex in e.nodes else unitColor
            initedEdges.append(graph_state.Edge(e.nodes, graph.externalVertex, colors=color))
        return Graph(initedEdges, externalVertex=graph.externalVertex)

    @staticmethod
    def _parseEdges(edgesIterable):
        edgesDict = dict()
        indexGenerator = 0
        for edge in edgesIterable:
            v1, v2 = edge.nodes
            iEdge = IndexableEdge(edge, indexGenerator)
            indexGenerator += 1
            Graph._insertEdge(edgesDict, v1, iEdge)
            if v1 != v2:
                Graph._insertEdge(edgesDict, v2, iEdge)
        return edgesDict

    @staticmethod
    def _persInsertEdge(edgesDict, edge):
        """
        persistent operation
        """
        vertexes = set(edge.nodes)
        for v in vertexes:
            Graph._insertEdge(edgesDict, v, edge)

    @staticmethod
    def _persDeleteEdge(edgesDict, edge):
        """
        persistent operation
        """
        vertexes = set(edge.nodes)
        for v in vertexes:
            Graph._deleteEdge(edgesDict, v, edge)

    @staticmethod
    def _insertEdge(edgesDict, vertex, edge):
        if vertex in edgesDict:
            edgesDict[vertex].append(edge)
        else:
            edgesDict[vertex] = [edge]

    @staticmethod
    def _deleteEdge(edgesDict, vertex, edge):
        try:
            edgeList = edgesDict[vertex]
            ieToRemove = None
            for ie in edgeList:
                if IndexableEdge.toIndexless(ie) == edge:
                    ieToRemove = ie
                    break
            edgeList.remove(ieToRemove)
            if not len(edgesDict[vertex]):
                del edgesDict[vertex]
        except AttributeError as e:
            raise ValueError(e), "edge not exists in graph"


class VertexTransformation(object):
    def __init__(self, mapping=None):
        """
        self._mapping - only non-identical index mappings
        """
        self._mapping = mapping if mapping else dict()

    @property
    def mapping(self):
        return self._mapping

    def add(self, anotherVertexTransformation):
        """
        composition of 2 transformations
        """
        composedMapping = dict()
        usedKeys = set()
        for k, v in self._mapping.items():
            av = anotherVertexTransformation._mapping.get(v, None)
            if av:
                composedMapping[k] = anotherVertexTransformation._mapping[v]
                usedKeys.add(v)
            else:
                composedMapping[k] = v
        for k, v in anotherVertexTransformation._mapping.items():
            if k not in usedKeys:
                composedMapping[k] = v
        return VertexTransformation(composedMapping)

    def map(self, vertexIndex):
        indexMapping = self._mapping.get(vertexIndex, None)
        if indexMapping:
            return indexMapping
        return vertexIndex


ID_VERTEX_TRANSFORMATION = VertexTransformation()
