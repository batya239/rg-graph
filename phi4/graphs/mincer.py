#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools

__author__ = 'mkompan'

import sys
import graphine
from graphine import filters
import graph_state
import methods.sdt_tools as sdt_tools

# no signs for momenta at this moment
topologies = {
    'e12-e3-45-45-5--': ('o4', ['Q', 'p6', 'p7', 'Q', 'p6', 'p1', 'p4', 'p2', 'p3', 'p5']),
    'e12-23-4-45-5-e-': ('la', ['Q', 'p1', 'p6', 'p7', 'p2', 'p5', 'p8', 'p3', 'p4', 'Q']),
    'e12-34-35-4-5-e-': ('be', ['Q', 'p1', 'p5', 'p6', 'p2', 'p8', 'p4', 'p7', 'p3', 'Q']),

}


def setMomenta(graphName, momentaList):
    graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % graphName))
    edgesList = list()
    for edge in graph.allEdges(withIndex=True):
        edge_ = copy.copy(edge.underlying)
        idx = edge.index
        edge_.colors = (momentaList[idx],)
        edgesList.append(edge_)
    return graphine.Graph(graph_state.GraphState(edgesList))


class Model(object):
    def __init__(self, n):
        self.n = n

    # noinspection PyUnusedLocal
    def isUVRelevant(self, edgesList, superGraph, superGraphEdges):
        subgraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
        return len(sdt_tools.internalEdges(subgraph)) == self.n


phi4 = Model(2)
subgraphUVFilters = filters.connected \
                    + filters.isUVRelevant(phi4)

#graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % sys.argv[1]))



def componentNodes(component):
    return reduce(lambda x, y: x | y, map(lambda x: set(x.nodes), component))


def connectedComponents(lines):
    components = list()
    for line in lines:
        connected = list()
        disconnected = list()
        nodes = set(line.nodes)
        for component in components:
            if len(nodes & componentNodes(component)) == 0:
                disconnected.append(component)
            else:
                connected.append(component)
        components = disconnected
        if len(connected)==0:
            components.append([line, ])
        else:
            components.append(reduce(lambda x, y: x + y, connected) + [line, ])
    return components


def shrinkComponents(graph, toShrink):
    shrinkedGraph = graph
    for component in toShrink:
        shrinkedGraph = shrinkedGraph.shrinkToPoint(component, renumbering=False)
    return shrinkedGraph


def FindTopology(graphName, topologies, n=2):
    for topology in topologies:

        graph = setMomenta(topology, topologies[topology][1])

        internalEdges = sdt_tools.internalEdges(graph)

        for lines in itertools.combinations(internalEdges, n):
            toShrink = connectedComponents(lines)
            shrinked = shrinkComponents(graph, toShrink)
            gsString = str(shrinked)
            if graphName == gsString[:gsString.find(":")]:
                return topologies[topology][0], shrinked
    return None


formTemplate = """
#-
#include mincer2.h
.global
Local F = 1{denom};
Multiply ep^3;
#call integral({topology})
Print +f;
.end
"""


def GenerateFormFile(topologyType, graphWithMomenta):
    denom = ""
    for line in sdt_tools.internalEdges(graphWithMomenta):
        denom += "/%s.%s" % (line.colors[0], line.colors[0])
    return formTemplate.format(denom=denom, topology=topologyType)


topologyType, graphWithMomenta = FindTopology(sys.argv[1], topologies)
f = open('form_files/%s.frm' % sys.argv[1], 'w')
f.write(GenerateFormFile(topologyType, graphWithMomenta))
f.close()
print topologyType, graphWithMomenta

