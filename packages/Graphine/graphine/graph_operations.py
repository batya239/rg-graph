#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
from graph_state import graph_state


def x1IrreducibleSubGraphs(graph):
    cache = dict()
    for subGraph in xSubGraphs(graph.allEdges(), externalVertex=graph.externalVertex, startSize=2):
        subGraphAsTuple = tuple(subGraph)
        isIrreducible = cache.get(subGraphAsTuple, None)
        if isIrreducible is None:
            isIrreducible = isGraph1Irreducible(subGraph, externalVertex=graph.externalVertex)
            cache[subGraphAsTuple] = isIrreducible
        if isIrreducible:
            yield subGraph


def xConnectedSubGraphs(graph):
    for subGraph in xSubGraphs(graph.allEdges(), graph.externalVertex):
        if len(subGraph) == 1 or isGraphConnected(subGraph, externalVertex=graph.externalVertex):
            yield subGraph


def xSubGraphs(edgesList, externalVertex, startSize=1):
    external, inner = pickExternalEdges(edgesList, externalVertex)

    innerLength = len(inner)

    if innerLength:
        for i in xrange(startSize, innerLength):
            for rawSubGraph in itertools.combinations(inner, i):
                subGraph = list(rawSubGraph)
                subGraphVertexes = set()
                for e in subGraph:
                    subGraphVertexes |= set(e.nodes)
                for e in supplement(inner, subGraph):
                    vSet = set(e.nodes)
                    vSetCard = len(vSet)
                    factor = 2 if vSetCard == 1 else 1
                    for v in vSet:
                        if v in subGraphVertexes:
                            subGraph += createExternalEdge(v, externalVertex, factor)
                for e in external:
                    v = [v for v in e.nodes if v != externalVertex][0]
                    if v in subGraphVertexes:
                        subGraph.append(e)
                yield subGraph


def isGraph1Irreducible(edgesList, externalVertex):
    """
    stupid algorithm
    """
    for e in edgesList:
        copiedEdges = copy.copy(edgesList)
        copiedEdges.remove(e)
        if not isGraphConnected(copiedEdges, externalVertex, set([v for v in e.nodes]) - set([externalVertex])):
            return False
    return True


def isGraphConnected(edgesList, externalVertex, additionalVertexes=set()):
    """
    graph as edges list
    """
    disjointSet = DisjointSet(additionalVertexes)

    for e in edgesList:
        v1, v2 = e.nodes
        if v1 == externalVertex or v2 == externalVertex:
            continue
        disjointSet.addKey(v1)
        disjointSet.addKey(v2)
        disjointSet.union(v1, v2)
    return disjointSet.isSimple()


def pickExternalEdges(edgesList, externalVertex=-1):
    inner = []
    external = []
    for e in edgesList:
        v1, v2 = e.nodes
        if v1 == externalVertex or v2 == externalVertex:
            external.append(e)
        else:
            inner.append(e)
    return external, inner


def createExternalEdge(innerVertex, externalVertex=-1, edgesCount=1):
    e = graph_state.Edge((externalVertex, innerVertex), external_node=externalVertex)
    return [e] * edgesCount


def supplement(aList, innerList):
    result = copy.copy(aList)
    for element in innerList:
        result.remove(element)
    return result


class DisjointSet(object):
    def __init__(self, keys=set()):
        self.underlying = dict()
        for k in keys:
            self.underlying[k] = k

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

    def union(self, a, b):
        """
        not fast implementation (no balancing)
        """
        if a is b:
            return
        aRoot = self.root(a)
        bRoot = self.root(b)
        if aRoot is not bRoot:
            self.underlying[aRoot] = bRoot

    def isSimple(self):
        roots = set()
        for key in self.underlying.keys():
            roots.add(self.root(key))
            if len(roots) != 1:
                return False
        return True
