#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'

import copy
import itertools
import graph_state
import graphine
import graph_util
import const
import diff_util
from rggraphutil import VariableAwareNumber
from graphine import filters, graph_operations


NULL_ARROW = graph_state.Arrow(graph_state.Arrow.NULL)


def pass_external_momentum(graph, filters=list()):
    result = set()
    for mp in x_pick_passing_external_momentum(graph, filters):
        result.add(pass_momentum_on_graph(graph, mp))
    return result


def x_pick_passing_external_momentum(graph, filters=list()):
    """
    chooses 2-combinations of external nodes
    """
    external_edges = graph.edges(graph.external_vertex)
    for edgesPair in itertools.combinations(_choose_external_edges_with_different_vertices(external_edges), 2):
        vertices = set()
        for e in edgesPair:
            vertices |= set(e.nodes)
        if len(vertices) == 3:
            tadpole = graph - external_edges
            if _check_valid(tadpole, vertices - set((graph.external_vertex,))):
                graph_with_momentum_passing = graph.change(external_edges, list(edgesPair))
                is_valid = True
                for f in filters:
                    if not f(graph_with_momentum_passing):
                        is_valid = False
                        break
                if is_valid:
                    yield max(edgesPair), min(edgesPair)


def _choose_external_edges_with_different_vertices(edges):
    used_vertices = set()
    result = []
    for e in edges:
        v = e.internal_nodes[0]
        if v not in used_vertices:
            used_vertices.add(v)
            result.append(e)
    return result


def pass_momentum_on_graph(graph, momentum_passing):
    assert len(momentum_passing) == 2
    edges_to_remove = list()
    copied_momentum_passing = list(momentum_passing)
    for e in graph.external_edges:
        if e in copied_momentum_passing:
            copied_momentum_passing.remove(e)
        else:
            edges_to_remove.append(e)
    return graph - edges_to_remove


def pseudo_pass_momentum_on_graph(graph, momentum_passing):
    return graph - graph.external_edges + momentum_passing


def arbitrarily_pass_momentum_with_preferable(graph, prefer_condition):
    preferred = list()
    not_preferred = list()
    for g in arbitrarily_pass_momentum(graph):
        if prefer_condition(g) and g not in preferred:
            preferred.append(g)
        elif g not in not_preferred:
            not_preferred.append(g)
    return preferred, not_preferred


def adjust(graph):
    to_add = list()
    graph -= graph.external_edges
    for v in graph.vertices:
        to_add_count = 4 - reduce(lambda s, e: s + (1 if len(set(e.nodes)) == 2 else 2), graph.edges(v), 0)
        assert to_add_count >= 0
        for i in xrange(to_add_count):
            to_add.append(graph_util.new_edge((graph.external_vertex, v), weight=const.ZERO_WEIGHT))
    return graph + to_add


def arbitrarily_pass_momentum(graph, pseudo=False):
    """
    find ALL (NO CONDITIONS) cases for momentum passing.
    """
    if pseudo and graph.external_edges_count != 2:
        graph = adjust(graph)
        if graph.external_edges_count == 1:
            return None

    if pseudo:
        graph = diff_util.find_minimal_momentum_passing(graph)

    result = set()

    if graph.internal_edges_count == 1 and len(graph.vertices) == 2:
        result.add(pseudo_pass_momentum_on_graph(graph, graph.external_edges)) if pseudo else result.add(graph)
        return result

    #ex-ex
    passing = set([x for x in x_pick_passing_external_momentum(graph)])
    for momentumPassing in passing:
        result.add(pseudo_pass_momentum_on_graph(graph, graph.external_edges) if pseudo else pass_momentum_on_graph(graph, momentumPassing))

    #ex-in
    external_vertex = graph.external_vertex
    external_edges = graph.edges(external_vertex)
    internal_vertices = graph.vertices - set(
        reduce(lambda x, y: x | y, map(lambda x: set(x.nodes), external_edges), set())
        - set([external_vertex])) - set([external_vertex])

    visited_vertices = set()
    has_arrows = graph.edges()[0].arrow is not None
    default_arrow = NULL_ARROW if has_arrows else None
    for e in external_edges:
        v = filter(lambda _v: _v != external_vertex, e.nodes)

        if v in visited_vertices:
            continue
        visited_vertices.add(v)

        edges_to_remove = list(external_edges)
        edges_to_remove.remove(e)
        _g = graph - edges_to_remove
        for v in internal_vertices:
            if _check_valid(_g, (v, e.internal_nodes[0])):
                new_external_edge = graph_util.new_edge((v, external_vertex),
                                                        external_node=external_vertex,
                                                        weight=const.ZERO_WEIGHT,
                                                        arrow=default_arrow)
                if pseudo:
                    result.add(pseudo_pass_momentum_on_graph(graph, (new_external_edge, e)))
                    continue
                graph_to_yield = _g + new_external_edge
                result.add(graph_to_yield)

    #in-in
    _g = graph - external_edges
    for vs in itertools.combinations(internal_vertices, 2):
        if _check_valid(_g, vs):
            new_edge1 = graph_util.new_edge((vs[0], external_vertex), external_node=external_vertex,
                                       weight=const.ZERO_WEIGHT, arrow=default_arrow)
            new_edge2 = graph_util.new_edge((vs[1], external_vertex), external_node=external_vertex,
                                       weight=const.ZERO_WEIGHT, arrow=default_arrow)
            if pseudo:
                result.add(pseudo_pass_momentum_on_graph(graph, (new_edge1, new_edge2)))
                continue
            result.add(_g + [new_edge1,
                             new_edge2])
    return result


def _check_valid(graph, new_external_vertices):
    for vertex in new_external_vertices:
        if not graph_state.operations_lib.is_graph_connected(filter(lambda e: vertex not in e.nodes, graph.edges())):
            return False
    for vertex in graph.vertices:
        components = graph_state.operations_lib.get_connected_components(graph.edges(), singular_vertices=(vertex,))
        if len(components) == 1:
            continue
        else:
            for component in components:
                has_external = False
                for new_external_vertex in new_external_vertices:
                    if new_external_vertex in component:
                        has_external = True
                if not has_external:
                    return False
    return True