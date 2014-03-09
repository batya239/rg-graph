#!/usr/bin/python
# -*- coding: utf8
import sys
import itertools

__author__ = 'mkompan'

import graph_state
from nickel import LEG


def sortString(string_):
    return "".join(sorted([x for x in string_]))


def isExternal(edge):
    return LEG in edge.nodes


def xSelections(items, n):
    if n == 0:
        yield []
    else:
        for i in xrange(len(items)):
            for ss in xSelections(items, n - 1):
                yield [items[i]] + ss


def splitEdges(edges):
    externalEdges = list()
    internalEdges = list()
    for edge in edges:
        if isExternal(edge):
            externalEdges.append(edge)
        else:
            internalEdges.append(edge)
    return externalEdges, internalEdges


def extractVertices(edges):
    vertexDict = dict()

    for edge in edges:
        if isExternal(edge):
            vertex = edge.nodes[1]
            field = edge.fields.pair[1]
            if vertex not in vertexDict:
                vertexDict[vertex] = []
            vertexDict[vertex].append(field)
        else:
            for i in range(2):
                vertex = edge.nodes[i]
                field = edge.fields.pair[i]
                if vertex not in vertexDict:
                    vertexDict[vertex] = []
                vertexDict[vertex].append(field)
        vertexDict_ = dict()
        for vertex in vertexDict:
            vertexDict_[vertex] = "".join(sorted(vertexDict[vertex]))
    return vertexDict_


def DynamicGraphs(edges, externalFields, lines, vertices):
    graphs = set()
    externalEdges, internalEdges = splitEdges(edges)


    if len(externalEdges) == len(externalFields):
        for extLegs in itertools.permutations(externalFields):
            new_ext_edges = list()
            xExtLegs = iter(extLegs)

            for edge in externalEdges:
                edge_ = gs_builder.new_edge(edge.nodes, fields=graph_state.Fields(('0', xExtLegs.next())))
                new_ext_edges.append(edge_)

            for fields in xSelections(lines, len(internalEdges)):
                new_edges = list()
                xFields = iter(fields)

                for edge in internalEdges:
                    edge_ = gs_builder.new_edge(edge.nodes, fields=graph_state.Fields([x for x in xFields.next()]))
                    new_edges.append(edge_)
                edges_ = graph_state.GraphState(new_edges+new_ext_edges).edges
                if len(set(extractVertices(edges_).values()) - vertices) == 0:
                    graphs.add(graph_state.GraphState(edges_))
        return graphs

    else:
        raise ValueError(
            "number of external legs (%s) different from externalFields (%s)" % (externalEdges, externalFields))


def chainTails(chain, forwardProp, backwardProp):
    if str(chain[0].fields) in forwardProp:
        start = chain[0].nodes[0]
    elif str(chain[0].fields) in backwardProp:
        start = chain[0].nodes[1]
    else:
        raise ValueError("invalid line in chain : %s" % chain[0])
    if str(chain[-1].fields) in forwardProp:
        end = chain[-1].nodes[1]
    elif str(chain[-1].fields) in backwardProp:
        end = chain[-1].nodes[0]
    else:
        raise ValueError("invalid line in chain : %s" % chain[-1])
    return start, end


def timeChains(graph, vertex, forwardProp, backwardProp):
    edges = graph.edges
    _timeChains = list([[]])
    flag = True
    while flag:
        for edge in edges:
            for chain in _timeChains:
                if str(edge.fields) not in forwardProp + backwardProp:
                    continue
                if edge in chain:
                    continue
                else:
                    start, end = chainTails(chain, forwardProp, backwardProp)
                    if len(set(edge.nodes) & set([start, end])) != 0:
                        pass
        return None


class TimeChainError(Exception):
    pass


def xChains(edges, forwardProp, backwardProp):
    # print "xChains", len(edges)
    if len(edges) == 0:
        yield []
    else:
        for i in xrange(len(edges)):
            edge = edges[i]
            # print edge
            for chain in xChains(edges[:i]+edges[i+1:], forwardProp, backwardProp):
                # print edge, chain, len(edges)
                if str(edge.fields) in forwardProp+backwardProp:
                    if len(chain) == 0:
                        yield chain+[edge]
                    else:
                        chainStart, chainEnd = chainTails(chain, forwardProp, backwardProp)
                        edgeStart, edgeEnd = chainTails([edge], forwardProp, backwardProp)
                        if edgeStart == chainEnd:
                            if edgeEnd == chainStart:
                                raise TimeChainError("time chain detected: %s, %s" % (chain, edge))
                            yield chain+[edge]
                        else:
                            yield chain
                else:
                    # print "yield", chain
                    yield chain

externalFields = [x for x in sys.argv[2]]

#lines = ['aA', 'Aa', 'aa']
lines = ['aA', 'Aa']
#vertices = set(map(sortString, ['Aaaa']))
vertices = set(map(sortString, ['aAa', 'AAa']))

from graph_util_mr import MAIN_GRAPH_CONFIG as gs_builder

edges = gs_builder.graph_state_from_str(sys.argv[1]).edges
#print edges

for graph in DynamicGraphs(edges, externalFields, lines, vertices):
    # print graph
    try:
        externalEdges, internalEdges = splitEdges(graph.edges)
        graphTimeChains = set([tuple(x) for x in xChains(internalEdges, ['aA'], ['Aa'])])
    except TimeChainError:
        # print "time loop:", graph
        continue

    print str(graph)+"::::"



