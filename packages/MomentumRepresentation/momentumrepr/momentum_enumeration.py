#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import propagator
import graph_state
import copy
import graphine
import itertools
import graph_util_mr
import uv
from rggraphutil import Ref


def find_momentum_enumeration_graph(graph, callback):
    loops_count = graph.getLoopsCount()
    tails_count = graph.externalEdgesCount()
    external_vertex = graph.external_vertex
    assert tails_count > 1
    empty_propagator = propagator.MomentumFlow.empty(tails_count, loops_count)
    graph_vertices = graph.vertices()

    def _enumerate_next_vertex(_graph, remaining_flows, vertex):
        if vertex not in graph_vertices:
            if not callback(_graph):
                raise StopIteration
            return
        result_known_flow = empty_propagator
        not_enumerated = list()
        for e in _graph.edges(vertex):
            if e.flow is not None:
                result_known_flow += e.flow if vertex == e.nodes[0] else - e.flow
            else:
                not_enumerated.append(e)
        if not len(not_enumerated):
            if result_known_flow != empty_propagator:
                return
            _enumerate_next_vertex(_graph, remaining_flows, vertex + 1)
            return

        if len(not_enumerated) == 1 and len(_graph.edges(vertex)) == 2:
            new_edges = copy.copy(_graph.allEdges())
            new_edges.remove(not_enumerated[0])
            new_edges.append(not_enumerated[0].copy(flow=-result_known_flow))
            new_graph = graphine.Graph(new_edges, external_vertex=external_vertex, renumbering=False)
            _enumerate_next_vertex(new_graph, remaining_flows, vertex + 1)

        for index, remaining_flow in enumerate(remaining_flows):
            if (not_enumerated[0].is_external() + remaining_flow.is_external()) % 2 == 0:
                if len(not_enumerated) == 1:
                    if result_known_flow + remaining_flow == empty_propagator:
                        new_remaining_flows = copy.copy(remaining_flows)
                        del new_remaining_flows[index]
                        new_edges = copy.copy(_graph.allEdges())
                        new_edges.remove(not_enumerated[0])
                        new_edges.append(not_enumerated[0].copy(flow=remaining_flow))
                        new_graph = graphine.Graph(new_edges, external_vertex=external_vertex, renumbering=False)
                        _enumerate_next_vertex(new_graph, new_remaining_flows, vertex + 1)
                else:
                    new_remaining_flows = copy.copy(remaining_flows)
                    del new_remaining_flows[index]
                    new_edges = copy.copy(_graph.allEdges())
                    new_edges.remove(not_enumerated[0])
                    new_edges.append(not_enumerated[0].copy(flow=remaining_flow))
                    new_graph = graphine.Graph(new_edges, external_vertex=external_vertex, renumbering=False)
                    _enumerate_next_vertex(new_graph, new_remaining_flows, vertex)
        pass

    one_part_flows = map(lambda i: propagator.MomentumFlow.single_internal(i, tails_count, loops_count), xrange(loops_count))
    one_part_flows += map(lambda f: -f, one_part_flows)
    all_flows = list(one_part_flows)
    for size in xrange(2, loops_count + 1):
        for comb in itertools.combinations(one_part_flows, size):
            result_flow = 0
            for e in comb:
                result_flow += e
            all_flows.append(result_flow)

    start_edges = copy.copy(graph.allEdges())
    es = graph.edges(graph.external_vertex)
    sum_external_flow = None
    with_external = list()
    for i in xrange(tails_count):
        external_edge = es[i]
        start_edges.remove(external_edge)
        if i != tails_count - 1:
            flow = propagator.MomentumFlow.single_external(i, tails_count, loops_count)
            sum_external_flow += flow
        else:
            flow = - sum_external_flow
        start_edges.append(external_edge.copy(flow=flow))
        for f in all_flows:
            with_external.append(f - flow)
            with_external.append(f + flow)

    all_flows += with_external

    try:
        _enumerate_next_vertex(graphine.Graph(start_edges), all_flows, 0)
    except StopIteration:
        pass


def is_suitable(graph):
    for sub_graph in graph.xRelevantSubGraphs(graphine.filters.oneIrreducible + uv.uv_condition):
        indices_in_co_subgraph = set()
        indices_in_subgraph = set()
        sub_graph_edges = sub_graph.allEdges()
        for e in graph.allEdges():
            if e.is_external():
                continue
            if e in sub_graph_edges:
                sub_graph_edges.remove(e)
                indices_in_subgraph |= e.flow.get_internal_momentas_indices()
            else:
                indices_in_co_subgraph |= e.flow.get_internal_momentas_indices()
        if len(indices_in_subgraph - indices_in_co_subgraph) != sub_graph.getLoopsCount():
            return False
    return True


def size_key(graph):
    _sum = 0
    for e in graph.allEdges():
        s = e.flow.size()
        if s > 2:
            _sum += s
    return _sum


def choose_minimal_momentum_flow(graph):
    minimal_suitable_graph = Ref.create()
    graphs = list()

    def chooser_graph_callback(g):
        if is_suitable(g):
            minimal_suitable_graph.set(g)
            return False
        else:
            graphs.append(g)
            return True

    find_momentum_enumeration_graph(graph, chooser_graph_callback)

    if minimal_suitable_graph is not None:
        return minimal_suitable_graph.get()

    if len(graphs):
        return graphs.sort(key=lambda e: e.flow.size())[0]

    return None