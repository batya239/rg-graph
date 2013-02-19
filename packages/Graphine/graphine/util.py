#!/usr/bin/python
# -*- coding: utf8


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