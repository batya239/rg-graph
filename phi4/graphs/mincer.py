#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools

__author__ = 'mkompan'

import sys
import graphine
import graph_state
import methods.sdt_tools as sdt_tools

# no signs for momenta at this moment
topologies = {
    'e12-23-3-e-': ('t1', ['Q', 'p1', 'p4', 'p5', 'p2', 'p3', 'Q']),
    'e12-e3-33--': ('t2', ['Q', 'p1', 'p2', 'Q', 'p1', 'p3', 'p4']),
    'e11-22-e-': ('t3', ['Q', 'p1', 'p2', 'p3', 'p4', 'Q']),
    'e12-e3-45-45-5--': ('o4', ['Q', 'p6', 'p7', 'Q', 'p6', 'p1', 'p4', 'p2', 'p3', 'p5']),
    'e12-23-4-45-5-e-': ('la', ['Q', 'p1', 'p6', 'p7', 'p2', 'p5', 'p8', 'p3', 'p4', 'Q']),
    'e12-34-35-4-5-e-': ('be', ['Q', 'p1', 'p5', 'p6', 'p2', 'p8', 'p4', 'p7', 'p3', 'Q']),
    'e12-34-34-e4--': ('bu', ['Q', 'p6', 'p7', 'p1', 'p4', 'p3', 'p5', 'Q', 'p2']),
    'e12-23-34-4-e-': ('fa', ['Q', 'p1', 'p5', 'p6', 'p2', 'p7', 'p4', 'p3', 'Q']),
    'e12-34-34-5-5-e-': ('no', ['Q', 'p1', 'p6', 'p2', 'p7', 'p8', 'p5', 'p3', 'p4', 'Q']),
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


def FindTopology(graphName, topologies):
    for topology in topologies:
        print "topology : ", topologies[topology][0]

        graph = setMomenta(topology, topologies[topology][1])

        internalEdges = sdt_tools.internalEdges(graph)

        graph_ = graphine.Graph(graph_state.GraphState.fromStr("%s::" % graphName))
        n = len(internalEdges) - len(sdt_tools.internalEdges(graph_))
        if n < 0:
            continue
        elif n == 0:
            if topology == graphName:
                return topologies[topology][0], graph

        for lines in itertools.combinations(internalEdges, n):
            shrinked = graph.batchShrinkToPoint([[x] for x in lines])
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


ans = FindTopology(sys.argv[1], topologies)
if ans is not None:
    topologyType, graphWithMomenta = ans
    f = open('form_files/%s.frm' % sys.argv[1], 'w')
    f.write(GenerateFormFile(topologyType, graphWithMomenta))
    f.close()
    print topologyType, graphWithMomenta
else:
    print "topology not found!"

