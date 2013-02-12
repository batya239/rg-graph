#!/usr/bin/python
# -*- coding: utf8


def getSubExternalVertexes(graph, subGraphAsList):
    subGraphVertexes = {}
    supplementGraph = graph.deleteEdges(subGraphAsList)
    for edge in subGraphAsList:
        subGraphVertexes += set(edge.nodes)
    supplementVertexes = supplementGraph.vertexes()
    return supplementVertexes - subGraphVertexes