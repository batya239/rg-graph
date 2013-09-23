#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
import graph_state
import graph

DEFAULT_EXTERNAL_LINE_FIELD = graph_state.Fields.fromStr("00")


# noinspection PyUnusedLocal
def isGraph1Irreducible(edgesList, superGraph, superGraphEdges):
    """
    stupid algorithm
    """
    for e in edgesList:
        copiedEdges = copy.copy(edgesList)
        copiedEdges.remove(e)
        if not _isGraphConnected(copiedEdges, superGraph.externalVertex,
                                 additionalVertexes=set([v for v in e.nodes]) - set([superGraph.externalVertex])):
            return False
    return True


# noinspection PyUnusedLocal
def isGraphVertexIrreducible(edgesList, superGraph, superGraphEdges):
    subGraph = graph.Representator.asGraph(edgesList, superGraph.externalVertex)
    if len(subGraph.vertexes() - set([superGraph.externalVertex])) == 1:
        return True
    if len(subGraph.vertexes()) == 2:
        return len(subGraph.allEdges()) - len(subGraph.edges(subGraph.externalVertex)) > 0
    for v in subGraph.vertexes():
        for e in subGraph.edges(v):
            if e.nodes[0] == e.nodes[1]:
                return False
        if v is not superGraph.externalVertex:
            if len(subGraph.vertexes()) == 2:
                return len(subGraph.allEdges()) - len(subGraph.edges(subGraph.externalVertex)) > 0
            else:
                edges = copy.copy(edgesList)
                for e in subGraph.edges(v):
                    edges.remove(e)
                additionalVertexes = subGraph.vertexes()
                additionalVertexes.remove(v)
                if not _isGraphConnected(edges, superGraph.externalVertex, additionalVertexes=additionalVertexes):
                    return False
    return True


def hasNoTadpolesInCounterTerm(edgesList, superGraph, superGraphEdges):
    if not len(edgesList):
        return False
    edges = copy.copy(superGraphEdges)
    singularVertexes = set()
    for e in edgesList:
        if e in edges:
            edges.remove(e)
        singularVertexes |= set(e.nodes)
    connectedComponents = _getConnectedComponents(edges, superGraph.externalVertex, singularVertexes=singularVertexes)
    for component in connectedComponents:
        allSingular = True
        for v in component:
            if not _DisjointSet.isSingular(v):
                allSingular = False
                break
        if allSingular:
            return False
        containsExternal = False
        for v in component:
            for e in superGraph.edges(v):
                if superGraph.externalVertex in e.nodes:
                    containsExternal = True
        if not containsExternal:
            return False
    return True


# noinspection PyUnusedLocal
def isGraphConnected(edgesList, superGraph, superGraphEdges):
    return _isGraphConnected(edgesList, superGraph.externalVertex)


def xSubGraphs(edgesList, edgesMap, externalVertex, cutEdgesToExternal=True, startSize=2, nextEdgeIndex=None):
    """
    cutEdgesToExternal - if True then all graphs from iterator hash only 2 external edges
    """
    external, inner = _pickExternalEdges(edgesList, externalVertex)

    innerLength = len(inner)

    if len(edgesList):
        hasColors = edgesList[0].colors is not None
        hasFields = edgesList[0].fields is not None

        #Are this shit?

        if startSize == 1:
            if not cutEdgesToExternal:
                raise AssertionError()
            notExternalVertexes = set(edgesMap.keys()) - set([externalVertex])
            for v in notExternalVertexes:
                edges = edgesMap.get(v, None)
                if edges:
                    subGraph = _createExternalEdge(v,
                                                   nextEdgeIndex=nextEdgeIndex,
                                                   externalVertex=externalVertex,
                                                   edgesCount=len(edges), hasColors=hasColors,
                                                   hasFields=hasFields,
                                                   defaultFields=DEFAULT_EXTERNAL_LINE_FIELD)
                    if nextEdgeIndex:
                        nextEdgeIndex += len(edges)
                    yield subGraph

        if innerLength:
            for i in xrange(max(2, startSize), innerLength):
                for rawSubGraph in itertools.combinations(inner, i):
                    subGraph = list(rawSubGraph)
                    subGraphVertexes = set()
                    for e in subGraph:
                        subGraphVertexes |= set(e.nodes)
                    if cutEdgesToExternal:
                        for e in _supplement(inner, subGraph):
                            vSet = set(e.nodes)
                            vSetCard = len(vSet)
                            factor = 2 if vSetCard == 1 else 1
                            for v in vSet:
                                if v in subGraphVertexes:
                                    subGraph += _createExternalEdge(v,
                                                                    externalVertex, factor,
                                                                    nextEdgeIndex=nextEdgeIndex,
                                                                    hasFields=hasFields,
                                                                    defaultFields=DEFAULT_EXTERNAL_LINE_FIELD,
                                                                    hasColors=hasColors)
                                    if nextEdgeIndex:
                                        nextEdgeIndex += factor
                    for e in external:
                        v = [v for v in e.nodes if v != externalVertex][0]
                        if v in subGraphVertexes:
                            subGraph.append(e)
                    yield subGraph


def _isGraphConnected(edgesList, externalVertex, additionalVertexes=set()):
    """
    graph as edges list
    """
    return len(_getConnectedComponents(edgesList, externalVertex, additionalVertexes)) == 1


def _getConnectedComponents(edgesList, externalVertex, additionalVertexes=set(), singularVertexes=set()):
    """
    graph as edges list
    """
    if externalVertex in additionalVertexes:
        additionalVertexes.remove(externalVertex)
    disjointSet = _DisjointSet(additionalVertexes)

    for e in edgesList:
        pair = e.nodes
        if externalVertex in pair:
            for v in set(pair) - set([externalVertex]):
                disjointSet.addKey(v)
            continue

        v = pair[0]
        if v in singularVertexes:
            pair = (disjointSet.nextSingularKey(v)), pair[1]
        v = pair[1]
        if v in singularVertexes:
            pair = pair[0], (disjointSet.nextSingularKey(v))

        disjointSet.union(pair)
    return disjointSet.getConnectedComponents()


def _pickExternalEdges(edgesList, externalVertex=-1):
    inner = []
    external = []
    for e in edgesList:
        v1, v2 = e.nodes
        if v1 == externalVertex or v2 == externalVertex:
            external.append(e)
        else:
            inner.append(e)
    return external, inner


def _createExternalEdge(innerVertex, externalVertex=-1, edgesCount=1,
                        hasColors=False, hasFields=False, defaultFields=None, nextEdgeIndex=None):
    colors = (0, 0) if hasColors else None
    fields = defaultFields if hasFields else None
    e = graph_state.Edge((externalVertex, innerVertex), external_node=externalVertex,
                                     colors=colors, fields=fields)
    if nextEdgeIndex is not None:
        e = graph.IndexAwareEdgeDelegate(e, nextEdgeIndex)
    return [e] * edgesCount


def _supplement(aList, innerList, check=False):
    result = copy.copy(aList)
    for element in innerList:
        if not check or element in result:
            result.remove(element)
    return result


class _DisjointSet(object):
    def __init__(self, keys=set()):
        self.underlying = dict()
        for k in keys:
            self.underlying[k] = k
        self.singularKeyPrefix = 1

    def addKey(self, key):
        if key not in self.underlying:
            self.underlying[key] = key

    def root(self, a):
        aRoot = a
        aNext = self.underlying[aRoot]
        while aNext != aRoot:
            aRoot = aNext
            aNext = self.underlying[aRoot]
        return aRoot

    def union(self, pair):
        """
        not fast implementation (no balancing)
        """
        a, b = pair
        self.addKey(a)
        self.addKey(b)
        if a is b:
            return
        aRoot = self.root(a)
        bRoot = self.root(b)
        if aRoot is not bRoot:
            self.underlying[aRoot] = bRoot

    def getConnectedComponents(self):
        connectedComponents = dict()
        for k in self.underlying.keys():
            kRoot = self.root(k)
            if kRoot in connectedComponents:
                connectedComponents[kRoot].append(k)
            else:
                connectedComponents[kRoot] = [k]
        return connectedComponents.values()

    def nextSingularKey(self, key):
        prefix = self.singularKeyPrefix
        self.singularKeyPrefix += 1
        return "__%s_%s" % (prefix, key)

    @staticmethod
    def isSingular(key):
        return str(key).startswith("__")