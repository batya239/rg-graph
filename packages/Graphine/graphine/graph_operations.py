#!/usr/bin/python
# -*- coding: utf8
import copy
import itertools
import graph_state
import graph


def from_graph_state_function(fun):
    def wrapper(graph):
        return fun(graph.edges())
    return wrapper


is_1_irreducible = from_graph_state_function(graph_state.operations_lib.is_1_irreducible)
is_connected = from_graph_state_function(graph_state.operations_lib.is_graph_connected)
is_vertex_irreducible = from_graph_state_function(graph_state.operations_lib.is_vertex_irreducible)


def has_tadpoles_in_counter_term(graph, super_graph):
    return graph_state.operations_lib.has_no_tadpoles_in_counter_term(graph.edges(), super_graph.edges())


def x_sub_graphs(graph, cut_edges_to_external=True, start_size=2):
    """
    cut_edges_to_external - if True then all graphs from iterator has only 2 external edges
    """
    if len(graph.edges()):
        external, inner = _pick_external_edges(graph.edges())
        inner_length = len(inner)

        if start_size == 1:
            if not cut_edges_to_external:
                raise AssertionError()
            not_external_vertices = graph.vertices - set([graph.external_vertex])
            for v in not_external_vertices:
                edges = graph.edges(v)
                if len(edges):
                    sub_graph = map(lambda e_: e_.copy(node_map={(set(e_.nodes)-set([v])).pop(): graph.external_vertex}),
                                    filter(lambda e: not e.is_external(), edges))
                    sub_graph += filter(lambda e: e.is_external(), edges)
                    yield sub_graph
        if inner_length:
            for i in xrange(max(2, start_size), inner_length):
                for raw_sub_graph in itertools.combinations(inner, i):
                    sub_graph = list(raw_sub_graph)
                    sub_graph_vertices = graph_state.operations_lib.get_vertices(sub_graph)
                    if cut_edges_to_external:
                        for e in _supplement(inner, sub_graph):
                            if len(e.internal_nodes) == 1:
                                pass
                            v_set = set(e.nodes)
                            for v in v_set:
                                if v in sub_graph_vertices:
                                    if len(v_set) == 1:
                                        sub_graph += e.cut_tadpole()
                                    else:
                                        sub_graph.append(e.copy({(set(e.nodes)-set([v])).pop(): graph.external_vertex}))
                    for e in external:
                        if e.internal_node in sub_graph_vertices:
                            sub_graph.append(e)
                    yield sub_graph


def _pick_external_edges(edges_list):
    inner = list()
    external = list()
    for e in edges_list:
        external.append(e) if e.is_external() else inner.append(e)
    return external, inner


def _supplement(a_list, inner_list, check=False):
    result = copy.copy(a_list)
    for element in inner_list:
        if not check or element in result:
            result.remove(element)
    return result