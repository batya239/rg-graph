#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


def _findMinimalExternalMomentumPassing(graph):
    externalEdges = graph.edges(graph.externalVertex)
    startVertex = externalEdges[0].internal_nodes[0]
    targetVertex = externalEdges[1].internal_nodes[0]
    queue = [startVertex]
    distanceMap = {startVertex: ()}
    while len(queue):
        vertex = queue[0]
        del queue[0]
        dist = distanceMap.get(vertex)
        for e in graph.edges(vertex):
            v = _chooseNotEqualsFromPair(e.nodes, vertex)
            eDist = distanceMap.get(v)
            newDist = 1 + len(dist)
            if eDist is None or len(eDist) > newDist:
                #
                # hack for fast
                #
                if v == targetVertex and newDist == 1:
                    return e,
                distanceMap[v] = (newDist, dist + (e,))
                queue.append(v)
    return distanceMap[targetVertex]


def _chooseNotEqualsFromPair(pair, element):
    if pair[0] == element:
        return pair[1]
    else:
        return pair[0]


def diffP2(graph):
    assert len(graph.edges(graph.externalVertex)) == 2
    minimalPassing = _findMinimalExternalMomentumPassing(graph)

class Propagator(object):
    """
    class Propagator represents expressions as
    """
    def __init__(self, delta, alpha=1, beta=0, gamma=0):
        assert gamma == 2 * (gamma / 2)
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        self._delta = delta

    def subsXi0AndAverage(self):
        """
        return sympy-like string
        """
        return "(({alpha})*p**({beta})*)"