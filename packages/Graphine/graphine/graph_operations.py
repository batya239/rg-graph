#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools


def x1IrreducibleSubGraphs(graph):
    cache = dict()
    for subGraph in xSubGraphs(graph.allEdges()):
        subGraphAsTuple = tuple(subGraph)
        isIrreducible = cache.get(subGraphAsTuple, None)
        if isIrreducible is None:
            isIrreducible = isGraph1Irreducible(subGraph)
            cache[subGraphAsTuple] = isIrreducible
        if isIrreducible:
            yield subGraph


def xConnectedSubGraphs(graph):
    for subGraph in xSubGraphs(graph.allEdges()):
        if isGraphConnected(subGraph):
            yield subGraph


def xSubGraphs(edgesList):
    listLength = len(edgesList)
    if listLength:
        for i in xrange(1, listLength - 1):
            for comb in itertools.combinations(edgesList, i):
                yield comb


def isGraph1Irreducible(edgesList):
    """
    stupid algorithm
    """
    for e in edgesList:
        copiedEdges = copy.copy(edgesList)
        copiedEdges.remove(e)
        if not isGraphConnected(copiedEdges):
            return False
    return True


def isGraphConnected(edgesList):
    """
    graph as edges list
    """
    disjointSet = DisjointSet()

    for e in edgesList:
        v1, v2 = e.nodes()
        disjointSet.addKey(v1)
        disjointSet.addKey(v2)
        disjointSet.union(v1, v2)
    return disjointSet.size() == 1


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
        if a is b: return
        aRoot = self.root(a)
        bRoot = self.root(b)
        if aRoot is not bRoot:
            self.underlying[aRoot] = bRoot

    def size(self):
        len(set(self.underlying.values()))