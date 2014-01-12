#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from graphine import Graph
import graph_state

new_edge = graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge


def graph_from_str(string,
                   do_init_color=False,
                   zeroColor=(0, 0),
                   unitColor=(1, 0),
                   do_init_arrow=False,
                   arrow_lines=None):
    g = Graph(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.graph_state_from_str(string))
    if do_init_color:
        g = init_colors(g, zeroColor, unitColor)
    if do_init_arrow:
        g = init_arrow(g, arrow_lines)
    return g


def init_colors(graph, zeroColor=graph_state.Rainbow((0, 0)), unitColor=graph_state.Rainbow((1, 0))):
    edges = graph.allEdges()
    initedEdges = list()
    for e in edges:
        if e.colors is None:
            color = zeroColor if graph.externalVertex in e.nodes else unitColor
            initedEdges.append(new_edge(e.nodes, graph.externalVertex, colors=color, arrow=e.arrow))
        else:
            initedEdges.append(e)
    return Graph(initedEdges, externalVertex=graph.externalVertex, renumbering=False)


def init_arrow(graph, arrow_lines):
    arrow_lines = list(arrow_lines)
    inited_edges = list()

    for e in graph.allEdges():
        nodes = e.nodes
        if nodes in arrow_lines:
            arrow_lines.remove(nodes)
            inited_edges.append(new_edge(e.nodes,
                                         external_node=graph.externalVertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.LEFT_ARROW),
                                         colors=e.colors,
                                         edge_id=e.edge_id))
            continue
        swapNodes = e.nodes[1], e.nodes[0]
        if swapNodes in arrow_lines:
            arrow_lines.remove(swapNodes)
            inited_edges.append(new_edge(swapNodes,
                                         external_node=graph.externalVertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.LEFT_ARROW),
                                         colors=e.colors,
                                         edge_id=e.edge_id))
            continue
        else:
            inited_edges.append(new_edge(e.nodes,
                                         external_node=graph.externalVertex,
                                         arrow=graph_state.Arrow(graph_state.Arrow.NULL),
                                         colors=e.colors,
                                         edge_id=e.edge_id))
    return Graph(inited_edges, externalVertex=graph.externalVertex, renumbering=False)


def batch_init_edges_colors(graphs, zeroColor=graph_state.Rainbow((0, 0)), unitColor=graph_state.Rainbow((1, 0))):
    return map(lambda g: init_colors(g, zeroColor, unitColor), graphs)
