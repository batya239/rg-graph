#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import propagator
import copy
import graphine
import itertools
import uv
from repoze.lru import LRUCache
from rggraphutil import Ref


def find_momentum_enumeration_graph(graph, callback):
    loops_count = graph.loops_count
    tails_count = graph.external_edges_count

    assert tails_count > 1
    empty_propagator = propagator.MomentumFlow.empty(tails_count, loops_count)
    graph_vertices = graph.vertices

    def _enumerate_next_vertex(_graph, remaining_flows, vertex):
        if vertex not in graph_vertices:
            internal_flows = set()
            for e in _graph:
                internal_flows |= set(e.flow.get_internal_momentas_indices())
            if len(internal_flows) != graph.loops_count:
                return
            if not callback(_graph):
                raise StopIteration
            return
        if not is_suitable(_graph, force=True):
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
            new_edges = list(_graph.edges())
            new_edges.remove(not_enumerated[0])
            new_edges.append(not_enumerated[0].copy(flow=-result_known_flow))
            new_graph = graphine.Graph(new_edges, renumbering=False)
            _enumerate_next_vertex(new_graph, remaining_flows, vertex + 1)

        for index, remaining_flow in enumerate(remaining_flows):
            if (not_enumerated[0].is_external() + remaining_flow.is_external()) % 2 == 0:
                if len(not_enumerated) == 1:
                    if result_known_flow + remaining_flow == empty_propagator:
                        new_remaining_flows = copy.copy(remaining_flows)
                        del new_remaining_flows[index]
                        new_edges = list(_graph.edges())
                        new_edges.remove(not_enumerated[0])
                        new_edges.append(not_enumerated[0].copy(flow=remaining_flow))
                        new_graph = graphine.Graph(new_edges, renumbering=False)
                        _enumerate_next_vertex(new_graph, new_remaining_flows, vertex + 1)
                else:
                    new_remaining_flows = copy.copy(remaining_flows)
                    del new_remaining_flows[index]
                    new_edges = list(_graph.edges())
                    new_edges.remove(not_enumerated[0])
                    new_edges.append(not_enumerated[0].copy(flow=remaining_flow))
                    new_graph = graphine.Graph(new_edges, renumbering=False)
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

    start_edges = list(graph.edges())
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
    all_flows = filter(lambda x: x.size(), all_flows)
    all_flows = sorted(all_flows, key=lambda x: x.size())
    try:
        _enumerate_next_vertex(graphine.Graph(start_edges), all_flows, 0)
    except StopIteration:
        pass


def is_suitable(graph, force=False):
    for sub_graph in graph.x_relevant_sub_graphs(graphine.filters.one_irreducible + uv.uv_condition):
        indices_in_co_subgraph = set()
        indices_in_subgraph = set()
        do_continue = False
        for e in sub_graph:
            f = e.flow
            if force and f is None:
                do_continue = True
                break
            if e.is_external():
                indices_in_co_subgraph |= f.get_internal_momentas_indices()
            else:
                indices_in_subgraph |= f.get_internal_momentas_indices()
        if do_continue:
            continue
        if len(indices_in_subgraph - indices_in_co_subgraph) != sub_graph.loops_count:
            return False
    return True


def size_key(graph):
    _sum = 0
    for e in graph.allEdges():
        s = e.flow.size()
        if s > 2:
            _sum += s
    return _sum


cache = LRUCache(1024)


def choose_minimal_momentum_flow(graph):
    print graph
    topology_key = graph.presentable_str
    momentum_representator = cache.get(topology_key, None)
    if momentum_representator is not None:
        result = apply_from_representator(graph, momentum_representator)
        assert result is not None
        return result

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
        result = minimal_suitable_graph.get()
        cache.put(topology_key, result)
        assert result is not None
        return result

    if len(graphs):
        result = graphs.sort(key=lambda e: e.flow.size())[0]
        cache.put(topology_key, result)
        assert result is not None
        return result

    assert False


def apply_from_representator(graph, representator):
    edges = list()
    for (original_e, representator_e) in itertools.izip(graph.edges(), representator.edges()):
        edges.append(original_e.copy(flow=representator_e.flow))
    return graphine.Graph(edges)