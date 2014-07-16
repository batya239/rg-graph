#!/usr/bin/python
# -*- coding: utf8
"""
provides tools to create filters for graph.Graph#x_relevant_sub_graphs method
"""
import graph_state


def graph_filter(qualifier):
    """
    graphFilter must be used as decorator of filter

    @graphFilter
    def myFilter(...):
      ...
    """
    return [qualifier]


def is_relevant(relevance_condition):
    """
    wrap functional class to function
    """
    def wrapper(edges_list, super_graph):
        return relevance_condition.is_relevant(edges_list, super_graph)

    return [wrapper]


def has_n_borders(n):
    """
    filter that condition is graph has n borders
    """
    @graph_filter
    def _has_n_borders(edges_list, super_graph):
        borders = set()
        for e in edges_list:
            if e.is_external():
                borders.add(e.internal_node)
        return len(borders) == n
    return _has_n_borders


def _graph_state_wrapper1(fun):
    def wrapper(edges_list, super_graph):
        return fun(edges_list)
    return wrapper


def _graph_state_wrapper2(fun):
    def wrapper(edges_list, super_graph):
        return fun(edges_list, super_graph.edges())
    return wrapper

#
# use this common filters
#
one_irreducible = graph_filter(_graph_state_wrapper1(graph_state.operations_lib.is_1_irreducible))
connected = graph_filter(_graph_state_wrapper1(graph_state.operations_lib.is_graph_connected))
no_tadpoles = graph_filter(_graph_state_wrapper2(graph_state.operations_lib.has_no_tadpoles_in_counter_term))
vertex_irreducible = graph_filter(_graph_state_wrapper1(graph_state.operations_lib.is_vertex_irreducible))
