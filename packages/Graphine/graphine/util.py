#!/usr/bin/python
# -*- coding: utf8
import graph_state
import graphine


def merge(graph1, graph2):
    """
    graph1 and graph2 - graphs with same topology

    function merge their colors into new graph

    ATTENTION: fields not taken into account
    """
    assert graph1.getPresentableStr() == graph2.getPresentableStr()
    edges1 = graph1.graphStateSortedEdges()
    edges2 = graph2.graphStateSortedEdges()
    newEdges = list()
    externalVertex = graph1.externalVertex
    for i in xrange(0, len(edges1)):
        newEdges.append(_mergeEdge(edges1[i], edges2[i], externalVertex=externalVertex))
    return graphine.Graph(newEdges, externalVertex=externalVertex)


def _mergeEdge(e1, e2, externalVertex):
    assert e1.nodes == e2.nodes
    return graph_state.Edge(e1.nodes, external_node=externalVertex, colors=e1.colors + e2.colors)


def getSubExternalVertexes(graph, subGraphAsList):
    """
    deprecated. doesn't tested !!!
    """
    subGraphVertexes = set()
    supplementGraph = graph.deleteEdges(subGraphAsList)
    for edge in subGraphAsList:
        subGraphVertexes |= set(edge.nodes)
    supplementVertexes = supplementGraph.vertexes()
    return supplementVertexes - subGraphVertexes


