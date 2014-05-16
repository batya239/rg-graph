#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from graphine import Graph
from rggraphutil import VariableAwareNumber
import graph_state
import const
import ir_uv

# new_edge = graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge
NEGATIVE_WEIGHT_EDGE = VariableAwareNumber("l", -1, 0)


def shrink_to_point(graph, sub_graphs):
    to_shrink = list()
    to_replace_by_edge = list()
    p2_counts = 0
    for sg in sub_graphs:
        edge = has_momentum_quadratic_divergence(sg)
        if edge is not None:
            to_replace_by_edge.append((edge, sg))
            graph = graph.change(sg.internal_edges, (edge,), renumbering=False)
            p2_counts += 1
        else:
            to_shrink.append(sg)
    shrunk = graph.batch_shrink_to_point(to_shrink)
    return shrunk, p2_counts


def has_momentum_quadratic_divergence(sub_graph):
    if sub_graph.external_edges_count != 2:
        return None

    subgraph_uv_index = ir_uv.uv_index(sub_graph)
    if subgraph_uv_index != 2:
        assert subgraph_uv_index < 2
        return None

    border_vertices = sub_graph.get_bound_vertices()
    assert len(border_vertices) == 2

    graph_str = str(sub_graph)
    arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
    arrow = graph_state.Arrow(graph_state.Arrow.NULL) if arrows_aware else None
    return new_edge(tuple(border_vertices), weight=NEGATIVE_WEIGHT_EDGE, arrow=arrow)


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
    edges = graph.edges()
    inited_edges = list()
    for e in edges:
        if e.weight is None:
            weight = zero_weight if graph.external_vertex in e.nodes else unit_weight
            inited_edges.append(new_edge(e.nodes, graph.external_vertex, weight=weight, marker=e.marker, arrow=e.arrow))
        else:
            inited_edges.append(e)
    return Graph(inited_edges, renumbering=False)


def init_arrow(graph, arrow_lines):
    arrow_lines = list(arrow_lines)
    inited_edges = list()

    for e in graph.edges():
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
    return Graph(inited_edges, renumbering=False)