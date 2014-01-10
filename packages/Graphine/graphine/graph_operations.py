#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
import graph_state
import graph

# noinspection PyUnusedLocal
def isGraph1Irreducible(edgesList, superGraph, superGraphEdges):
    """
    stupid algorithm
    """
    for e in edgesList:
        if e.is_external():
            continue
        copiedEdges = copy.copy(edgesList)
        copiedEdges.remove(e)
        if not _is_graph_connected(copiedEdges, superGraph.externalVertex,
                                   additionalVertexes=set([v for v in e.nodes]) - set([superGraph.externalVertex])):
            return False
    return True


# noinspection PyUnusedLocal
def isGraphVertexIrreducible(edgesList, superGraph, superGraphEdges):
    subGraph = graph.Representator.asGraph(edgesList, superGraph.externalVertex)
    if len(subGraph.vertices() - set([superGraph.externalVertex])) == 1:
        return True
    if len(subGraph.vertices()) == 2:
        return len(subGraph.allEdges()) - len(subGraph.edges(subGraph.externalVertex)) > 0
    for v in subGraph.vertices():
        for e in subGraph.edges(v):
            if e.nodes[0] == e.nodes[1]:
                return False
        if v is not superGraph.externalVertex:
            if len(subGraph.vertices()) == 2:
                return len(subGraph.allEdges()) - len(subGraph.edges(subGraph.externalVertex)) > 0
            else:
                edges = copy.copy(edgesList)
                for e in subGraph.edges(v):
                    edges.remove(e)
                additionalVertexes = set(subGraph.vertices())
                additionalVertexes.remove(v)
                if not _is_graph_connected(edges, superGraph.externalVertex, additionalVertexes=additionalVertexes):
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
    connectedComponents = _get_connected_components(edges, superGraph.externalVertex, singularVertexes=singularVertexes)
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
    return _is_graph_connected(edgesList, superGraph.externalVertex)


def _default_external_edge_creation_strategy(adjacency_edges, vertex, externalVertex):
    has_colors = adjacency_edges[0].colors is not None
    has_fields = adjacency_edges[0].fields is not None
    colors = graph_state.Rainbow((0, 0)) if has_colors else None
    fields = graph_state.Fields.fromStr("00") if has_fields else None
    return graph_state.Edge((externalVertex, vertex),
                            external_node=externalVertex,
                            colors=colors,
                            fields=fields)


def x_sub_graphs(edges_list, edges_map, external_vertex,
                 cut_edges_to_external=True,
                 external_edge_creation_strategy=None,
                 start_size=2):
    """
    cut_edges_to_external - if True then all graphs from iterator has only 2 external edges
    """
    if external_edge_creation_strategy is None:
        external_edge_creation_strategy = _default_external_edge_creation_strategy
    external, inner = _pick_external_edges(edges_list, external_vertex)
    inner_length = len(inner)

    if len(edges_list):
        if start_size == 1:
            if not cut_edges_to_external:
                raise AssertionError()
            notExternalVertexes = set(edges_map.keys()) - set([external_vertex])
            for v in notExternalVertexes:
                edges = edges_map.get(v, None)
                if edges:
                    externalEdges = filter(lambda e: len(e.internal_nodes) == 1, edges)
                    subGraph = [external_edge_creation_strategy(edges_map[v], v, external_vertex)] * (len(edges) - len(externalEdges))
                    subGraph += externalEdges
                    yield subGraph

        if inner_length:
            for i in xrange(max(2, start_size), inner_length):
                for rawSubGraph in itertools.combinations(inner, i):
                    subGraph = list(rawSubGraph)
                    subGraphVertexes = set()
                    for e in subGraph:
                        subGraphVertexes |= set(e.nodes)
                    if cut_edges_to_external:
                        for e in _supplement(inner, subGraph):
                            if len(e.internal_nodes) == 1:
                                pass
                            vSet = set(e.nodes)
                            for v in vSet:
                                if v in subGraphVertexes:
                                    factor = 2 if len(vSet) == 1 else 1
                                    subGraph.append(external_edge_creation_strategy(edges_map[v], v, external_vertex))
                    for e in external:
                        v = e.internal_nodes[0]
                        if v in subGraphVertexes:
                            subGraph.append(e)
                    yield subGraph


def _is_graph_connected(edgesList, externalVertex, additionalVertexes=set()):
    """
    graph as edges list
    """
    return len(_get_connected_components(edgesList, externalVertex, additionalVertexes)) == 1


def _get_connected_components(edgesList, externalVertex, additionalVertexes=set(), singularVertexes=set()):
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


def _pick_external_edges(edgesList, externalVertex=-1):
    inner = []
    external = []
    for e in edgesList:
        v1, v2 = e.nodes
        if v1 == externalVertex or v2 == externalVertex:
            external.append(e)
        else:
            inner.append(e)
    return external, inner


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