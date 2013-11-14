#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'


import itertools


def find_topology(target_graph, topologies):
    """
    finds correct topology for target_graph

    topology - Graph, tuple
    """
    target_graph_name = target_graph.getPresentableStr()
    for topology in topologies:
        model_graph = topologies[0]
        internal_edges = model_graph.internalEdges()
        n = len(internal_edges) - len(target_graph.internalEdges())
        if n < 0:
            continue
        elif n == 0:
            if topology == target_graph_name:
                yield topologies[topology][0], model_graph

        for lines in itertools.combinations(internal_edges, n):
            shrunk = model_graph.batchShrinkToPoint([[x] for x in lines])
            gs_as_str = shrunk.getPresentableStr()
            if target_graph_name == gs_as_str:
                yield topologies[topology][0], topologies[1] + tuple(map(lambda e: e.colors[0], lines))


def choose_max(graphs):
    assert len(graphs)

    def compare(graph1, graph2):
        """
        Laporta comparator
        """
        n1 = graph1.internalEdges()
        n2 = graph2.internalEdges()
        sub = n1 - n2
        if sub != 0:
            return sub
        md1 = reduce(lambda e: e.colors[0] - 1, graph1.internalEdges())
        md2 = reduce(lambda e: e.colors[0] - 1, graph2.internalEdges())
        sub = md1 - md2
        return sub

    return max(graphs, compare)[0]
