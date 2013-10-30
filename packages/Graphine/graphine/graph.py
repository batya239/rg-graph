#!/usr/bin/python
# -*- coding: utf8
import copy
import graph_state
import rggraphutil
import graph_operations
import itertools

assert graph_state.Edge.CREATE_EDGES_INDEX


class Representator(object):
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


class _IdAwareEdgeDelegate(object):
    """
    DO NOT USE IT OUTSIDE THIS PACKAGE

    used for comparing edges by id
    """
    def __init__(self, edge):
        self._edge = edge

    @property
    def edge(self):
        return self._edge

    def __hash__(self):
        return hash(self.edge.edge_id)

    def __eq__(self, other):
        return self.edge.edge_id == other.edge.edge_id


class Graph(object):
    """
    representation of graph
    """
    def __init__(self, obj, externalVertex=-1, renumbering=True):
        """
        self.edges - dict where keys is one vertex of edge and value is list of second vertices
        """
        if isinstance(obj, list):
            self._edges = Graph._parseEdges(graph_state.GraphState(obj).edges if renumbering else obj)
        elif isinstance(obj, dict):
            self._edges = obj
        elif isinstance(obj, graph_state.GraphState):
            self._edges = Graph._parseEdges(obj.edges)
        self._nextVertexIndex = max(self._edges.keys()) + 1
        self._externalVertex = externalVertex
        self._hash = None
        self._loopsCount = None
        self._externalEdges = None
        self._graphState = None
        self._allEdges = None
        self._allEdgesIndices = None
        self._allInternalEdgesCount = None
        self._boundVertexes = None
        self._vertices = None

    @property
    def externalVertex(self):
        return self._externalVertex

    def externalEdges(self):
        if self._externalEdges is None:
            self._externalEdges = self.edges(self.externalVertex)
        return self._externalEdges

    def externalEdgesCount(self):
        return len(self.externalEdges())

    def internalEdges(self):
        res = list()
        for edge in self.allEdges():
            if self.externalVertex not in edge.nodes:
                res.append(edge)
        return res

    def vertices(self):
        if self._vertices is None:
            self._vertices = frozenset(self._edges.keys())
        return self._vertices

    def createVertexIndex(self):
        to_return = self._nextVertexIndex
        self._nextVertexIndex += 1
        return to_return

    def edges(self, vertex, vertex2=None):
        if vertex2 is None:
            return copy.copy(self._edges.get(vertex, []))
        return filter(lambda e: vertex2 in e.nodes, self._edges.get(vertex, []))

    def allEdgesIndices(self):
        """
        special method, inserted to Graph for caching
        """
        if self._allEdgesIndices is None:
            self._allEdgesIndices = frozenset(map(lambda e: e.edge_id, self.allEdges()))
        return self._allEdgesIndices

    def allEdges(self, nickel_ordering=False):
        if nickel_ordering:
            return self.toGraphState().edges
        if self._allEdges is None:
            wrapped_result = set()
            for edges in self._edges.values():
                for e in edges:
                    wrapped_result.add(_IdAwareEdgeDelegate(e))
            self._allEdges = map(lambda ei: ei.edge, wrapped_result)
        return self._allEdges

    def addEdges(self, edgesToAdd):
        """
        immutable operation
        """
        newEdges = self.allEdges() + edgesToAdd
        return Graph(newEdges, externalVertex=self.externalVertex)

    def addEdge(self, edge):
        return self.addEdges([edge])

    def deleteEdges(self, edgesToRemove):
        """
        immutable operation
        """
        newEdges = copy.deepcopy(self._edges)
        for edge in edgesToRemove:
            Graph._persDeleteEdge(newEdges, edge)
        return Graph(newEdges, externalVertex=self.externalVertex)

    def change(self, edgesToRemove=None, edgesToAdd=None):
        """
        transactional changes graph structure
        """
        newEdges = copy.deepcopy(self.allEdges())
        map(lambda e: newEdges.remove(e), edgesToRemove)
        map(lambda e: newEdges.append(e), edgesToAdd)
        return Graph(newEdges, externalVertex=self.externalVertex)

    def deleteVertex(self, vertex, transformEdgesToExternal=False):
        assert vertex != self.externalVertex
        if transformEdgesToExternal:
            edges = self.edges(vertex)
            for e in edges:
                if self.externalVertex in e.nodes:
                    raise AssertionError
            g = self.deleteEdges(edges)
            nodeMap = {vertex: self.externalVertex}
            nEdges = map(lambda e: e.copy(nodeMap), edges)
            return g.addEdges(nEdges)
        else:
            return self.deleteEdges(self.edges(vertex))

    def deleteEdge(self, edge):
        return self.deleteEdges([edge])

    def contains(self, other_graph):
        self_edges = self._edges
        other_edges = other_graph._edges
        for v, other_es in other_edges.iteritems():
            _self_es = self_edges.get(v, None)
            if _self_es is None and len(other_edges):
                return False
            self_es = copy.copy(_self_es)
            for e in other_es:
                if e in self_es:
                    self_es.remove(e)
                else:
                    return False
        return True

    def batchShrinkToPointWithAuxInfo(self, sub_graphs):
        """
        subGraphs -- list of graphs edges or graph with equivalent numbering of vertices
        """
        if not len(sub_graphs):
            return self, list()

        vertex_transformation = ID_VERTEX_TRANSFORMATION
        g = self
        new_vertices = list()
        for subGraph in sub_graphs:
            all_edges = subGraph.allEdges() if isinstance(subGraph, Graph) else subGraph
            g, new_vertex, vertex_transformation = g._shrinkToPoint(all_edges, vertex_transformation)
            new_vertices.append(new_vertex)
        assert g
        return g, new_vertices

    def batchShrinkToPoint(self, sub_graphs):
        return self.batchShrinkToPointWithAuxInfo(sub_graphs)[0]

    def _shrinkToPoint(self, unTransformedEdges, vertex_transformation=None):
        """
        obj -- list of edges or graph
        immutable operation
        """
        if not vertex_transformation:
            vertex_transformation = ID_VERTEX_TRANSFORMATION

        edges = map(lambda e: e.copy(vertex_transformation.mapping), unTransformedEdges)

        newRawEdges = copy.copy(self.allEdges())
        markedVertexes = set()
        for edge in edges:
            v1, v2 = edge.nodes
            if v1 != self.externalVertex and v2 != self.externalVertex:
                newRawEdges.remove(edge)
                markedVertexes.add(v1)
                markedVertexes.add(v2)

        newEdges = []
        currVertexTransformationMap = dict()
        for edge in newRawEdges:
            v1, v2 = edge.nodes
            copy_map = {}
            if v1 in markedVertexes:
                currVertexTransformationMap[v1] = self._nextVertexIndex
                copy_map[v1] = self._nextVertexIndex
            if v2 in markedVertexes:
                currVertexTransformationMap[v2] = self._nextVertexIndex
                copy_map[v2] = self._nextVertexIndex
            if len(copy_map):
                newEdges.append(edge.copy(copy_map))
            else:
                newEdges.append(edge)
        return Graph(newEdges, externalVertex=self.externalVertex, renumbering=False), \
               self._nextVertexIndex, \
               vertex_transformation.add(VertexTransformation(currVertexTransformationMap))

    def shrinkToPoint(self, edges):
        return self._shrinkToPoint(edges)[0]

    def shrinkToPointWithAuxInfo(self, edges):
        return self._shrinkToPoint(edges)[0:2]

    def xRelevantSubGraphs(self,
                           filters=list(),
                           resultRepresentator=Representator.asGraph,
                           cutEdgesToExternal=True,
                           exact=True):
        allEdges = self.allEdges()
        simpleCache = dict()
        exactSubGraphIterator = graph_operations.xSubGraphs(allEdges,
                                                            self._edges,
                                                            self.externalVertex,
                                                            cutEdgesToExternal=cutEdgesToExternal)
        sgIterator = exactSubGraphIterator if exact else itertools.chain(exactSubGraphIterator, (allEdges,))
        for subGraphAsList in sgIterator:
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

    def graphStateSortedEdges(self):
        return self.toGraphState().edges

    def toGraphState(self):
        if self._graphState is None:
            self._graphState = graph_state.GraphState(self.allEdges(nickel_ordering=False))
        return self._graphState

    def getBoundVertexes(self):
        if self._boundVertexes is None:
            self._boundVertexes = set()
            for e in self.edges(self.externalVertex):
                self._boundVertexes.add(e.internal_nodes[0])
        return self._boundVertexes

    def getAllInternalEdgesCount(self):
        if self._allInternalEdgesCount is None:
            internalEdgesCount = 0
            for v, e in self._edges:
                internalEdgesCount += len(e)
            self._allInternalEdgesCount = internalEdgesCount / 2 - len(self._edges[self.externalVertex])
        return self._allInternalEdgesCount

    def getLoopsCount(self):
        if self._loopsCount is None:
            externalLegsCount = len(self.edges(self.externalVertex))
            self._loopsCount = len(self.allEdges()) - externalLegsCount - (len(self.vertices()) -
                                                                           (1 if externalLegsCount != 0 else 0)) + 1
        return self._loopsCount

    def getPresentableStr(self):
        asStr = str(self)
        return asStr[:asStr.index("::")]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.toGraphState())

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.toGraphState()) + 37 * hash(self.vertices())
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return False
        return self.toGraphState() == other.toGraphState() and self.vertices() == other.vertices()

    @staticmethod
    def fromStr(string,
                initEdgesColor=False,
                zeroColor=(0, 0),
                unitColor=(1, 0),
                initFields=False,
                fieldLines=None,
                fieldValue=None,
                noFieldValue=None):
        g = Graph(graph_state.GraphState.fromStr(string))
        if initEdgesColor:
            g = Graph.initEdgesColors(g, zeroColor, unitColor)
        if initFields:
            g = Graph.initFields(g, fieldLines, fieldValue, noFieldValue)
        return g

    @staticmethod
    def initEdgesColors(graph, zeroColor=(0, 0), unitColor=(1, 0)):
        edges = graph.allEdges()
        initedEdges = list()
        for e in edges:
            if e.colors is None:
                color = zeroColor if graph.externalVertex in e.nodes else unitColor
                initedEdges.append(graph_state.Edge(e.nodes, graph.externalVertex, colors=color, fields=e.fields))
            else:
                initedEdges.append(e)
        return Graph(initedEdges, externalVertex=graph.externalVertex, renumbering=False)

    @staticmethod
    def initFields(graph, fieldLines, fieldValue, noFieldValue):
        """
        numeratorLines is list of pair, where pair first is from pair second is to
        """
        fieldLines = list(fieldLines)
        initedEdges = list()

        for e in graph.allEdges():
            nodes = e.nodes
            if nodes in fieldLines:
                fieldLines.remove(nodes)
                initedEdges.append(graph_state.Edge(e.nodes,
                                                    external_node=graph.externalVertex,
                                                    fields=fieldValue,
                                                    colors=e.colors,
                                                    edge_id=e.edge_id))
                continue
            swapNodes = e.nodes[1], e.nodes[0]
            if swapNodes in fieldLines:
                fieldLines.remove(swapNodes)
                initedEdges.append(graph_state.Edge(swapNodes,
                                                    external_node=graph.externalVertex,
                                                    fields=fieldValue,
                                                    colors=e.colors,
                                                    edge_id=e.edge_id))
                continue
            else:
                initedEdges.append(graph_state.Edge(e.nodes,
                                                    external_node=graph.externalVertex,
                                                    fields=noFieldValue,
                                                    colors=e.colors,
                                                    edge_id=e.edge_id))
        return Graph(initedEdges, externalVertex=graph.externalVertex, renumbering=False)

    @staticmethod
    def batchInitEdgesColors(graphs, zeroColor=(0, 0), unitColor=(1, 0)):
        return map(lambda g: Graph.initEdgesColors(g, zeroColor, unitColor), graphs)

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
    def _persInsertEdge(edgesDict, edge):
        """
        persistent operation
        """
        vertices = set(edge.nodes)
        for v in vertices:
            Graph._insertEdge(edgesDict, v, edge)

    @staticmethod
    def _persDeleteEdge(edgesDict, edge):
        """
        persistent operation
        """
        vertices = set(edge.nodes)
        for v in vertices:
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
            edgeList.remove(edge)
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
            av = anotherVertexTransformation.mapping.get(v, None)
            if av:
                composedMapping[k] = anotherVertexTransformation.mapping[v]
                usedKeys.add(v)
            else:
                composedMapping[k] = v
        for k, v in anotherVertexTransformation.mapping.items():
            if k not in usedKeys:
                composedMapping[k] = v
        return VertexTransformation(composedMapping)

    def map(self, vertexIndex):
        indexMapping = self._mapping.get(vertexIndex, None)
        if indexMapping:
            return indexMapping
        return vertexIndex


ID_VERTEX_TRANSFORMATION = VertexTransformation()