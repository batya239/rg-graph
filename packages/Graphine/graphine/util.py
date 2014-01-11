#!/usr/bin/python
# -*- coding: utf8
import graph_state
import graph


def init_graph_colors_with_default_values_if_need(g, default_internal_color, default_external_color):
    all_edges = g.allEdges(nickel_ordering=True)
    not_none_colors = 0
    for e in all_edges:
        if e.colors is not None:
            not_none_colors += 1
    if not_none_colors == len(all_edges):
        return g
    assert not_none_colors == 0
    new_edges = map(lambda e: graph_state.Edge(e.nodes, colors=default_external_color if e.is_external() else default_internal_color), g.allEdges(nickel_ordering=True))
    external_vertex = g.externalVertex
    return graph.Graph(new_edges, externalVertex=external_vertex)


def has_intersecting_by_vertexes_graphs(graphs):
    """
    return True if some of graphs hash non-trivial intersection on vertexes
    """
    if not len(graphs):
        return False
    unique_vertices = set()
    for g in graphs:
        internal_vertices = g.vertices() - set([g.externalVertex])
        current_unique_vertices_size = len(unique_vertices)
        unique_vertices |= internal_vertices
        if len(unique_vertices) != current_unique_vertices_size + len(internal_vertices):
            return True
    return False


def merge(graph1, graph2):
    """
    graph1 and graph2 - graphs with same topology

    function merge their colors into new graph

    ATTENTION: fields not taken into account
    """
    assert graph1.getPresentableStr() == graph2.getPresentableStr()
    edges1 = graph1.allEdges(nickel_ordering=True)
    edges2 = graph2.allEdges(nickel_ordering=True)
    new_edges = list()
    external_vertex = graph1.externalVertex
    for i in xrange(0, len(edges1)):
        new_edges.append(_merge_edge(edges1[i], edges2[i], external_vertex=external_vertex))
    return graph.Graph(new_edges, externalVertex=external_vertex)


def _merge_edge(e1, e2, external_vertex):
    assert e1.nodes == e2.nodes
    return graph_state.Edge(e1.nodes, external_node=external_vertex, colors=e1.colors + e2.colors)
