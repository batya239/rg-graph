#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from graphine import Graph
from rggraphutil import VariableAwareNumber
import graph_state
import const

new_edge = graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge


def graph_from_str(string,
                   do_init_weight=False,
                   zero_weight=const.ZERO_WEIGHT, 
                   unit_weight=const.UNIT_WEIGHT,
                   do_init_arrow=False,
                   arrow_lines=None):
    g = Graph(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.graph_state_from_str(string))
    if do_init_weight:
        g = init_weight(g, zero_weight, unit_weight)
    if do_init_arrow:
        g = init_arrow(g, arrow_lines)
    return g


def batch_init_edges_weight(graphs, zero_weight=const.ZERO_WEIGHT, unit_weight=const.UNIT_WEIGHT):
    return map(lambda g: init_weight(g, zero_weight, unit_weight), graphs)


def init_weight(graph, zero_weight=const.ZERO_WEIGHT, unit_weight=const.UNIT_WEIGHT):
    edges = graph.allEdges()
    inited_edges = list()
    for e in edges:
        if e.weight is None:
            weight = zero_weight if graph.external_vertex in e.nodes else unit_weight
            inited_edges.append(new_edge(e.nodes, graph.external_vertex, weight=weight, marker=e.marker, arrow=e.arrow))
        else:
            inited_edges.append(e)
    return Graph(inited_edges, external_vertex=graph.external_vertex, renumbering=False)


def init_arrow(graph, arrow_lines):
    arrow_lines = list(arrow_lines)
    inited_edges = list()

    for e in graph.allEdges():
        nodes = e.nodes
        if nodes in arrow_lines:
            arrow_lines.remove(nodes)
            inited_edges.append(new_edge(e.nodes,
                                         external_node=graph.external_vertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.LEFT_ARROW),
                                         weight=e.weight,
                                         marker=e.marker,
                                         edge_id=e.edge_id))
            continue
        swapped_nodes = e.nodes[1], e.nodes[0]
        if swapped_nodes in arrow_lines:
            arrow_lines.remove(swapped_nodes)
            inited_edges.append(new_edge(swapped_nodes,
                                         external_node=graph.external_vertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.LEFT_ARROW),
                                         weight=e.weight,
                                         marker=e.marker,
                                         edge_id=e.edge_id))
            continue
        else:
            inited_edges.append(new_edge(e.nodes,
                                         external_node=graph.external_vertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.NULL),
                                         weight=e.weight,
                                         marker=e.marker,
                                         edge_id=e.edge_id))
    return Graph(inited_edges, external_vertex=graph.external_vertex, renumbering=False)