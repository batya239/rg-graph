#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import uv
import graphine
import propagator
import time_versions
import graph_util
import diff_util
import representation
import propagator
import map_reduce_wrapper
import integration
from rggraphutil import emptyListDict

no_tadpoles = graphine.filters.noTadpoles
one_irreducible = graphine.filters.oneIrreducible


def kr1_log_divergence(graph_state_as_str):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str)


def kr1_d_p2(graph_state_as_str):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, diff_util.D_p2)


def kr1_d_iw(graph_state_as_str):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, diff_util.D_i_omega)


def kr1_with_some_additional_lambda_operation(graph_state_as_str, additional_lambda=None):
    def integral_producer_lambda(graph_with_tv, coeff):
        base_integrand = integration.get_base_integrand(graph_with_tv) * coeff
        loop_momentum_vars = integration.get_loop_momentum_vars(graph_with_tv)
        stretch_vars = integration.get_stretch_vars(graph_with_tv)
        angles = integration.get_angles(graph_with_tv)
        return integration.construct_integrand(base_integrand, loop_momentum_vars, stretch_vars, angles)

    graph = graph_util.from_str(graph_state_as_str)
    graph = map_reduce_wrapper.MapReduceAlgebraWrapper(graph)
    graph = graph.apply(diff_util.D_minus_tau)
    if additional_lambda is not None:
        graph = graph.apply(additional_lambda)
    graph = graph.apply(representation.enumerate_propagators)
    graph = graph.apply(propagator.subs_external_propagators_is_zero)
    graph = graph.apply(kr1_stretching)
    integrals = graph.map_with_coefficients(integral_producer_lambda)
    return integrals



def kr1_stretching(graph):
    uv_subgraphs = graph.xRelevantSubGraphs(one_irreducible + no_tadpoles + uv.uv_condition)
    graphs_and_time_versions = time_versions.find_time_versions(graph)

    with_stretching = list()
    stretchers_for_edges = emptyListDict()
    for graph_and_tv in graphs_and_time_versions:
        g = graph_and_tv.graph
        for uv_graph in uv_subgraphs:
            add_stretching(g, uv_graph, graph_and_tv.edges_cross_sections, stretchers_for_edges)

        new_edges = list()
        for e in g.allEdges():
            stretchers = stretchers_for_edges[RefEqualityWrapper(e)]
            _e = e
            for s in stretchers:
                _e = _e.copy(flow=_e.flow.stretch(s))
            new_edges.append(_e)

        with_stretching.append(graph_and_tv.set_graph(graphine.Graph(new_edges, g.external_vertex)))

    return with_stretching


def add_stretching(graph, uv_sub_graph, cross_sections, stretchers_for_edges):
    cross_sections_base_number = len(uv_sub_graph.vertices()) - 2
    base_uv_index = uv.uv_index(uv_sub_graph)

    cross_sections_number = 0
    for cs in cross_sections:
        intersect = False
        sub_graph_edges = set(uv_sub_graph.allEdges())
        for e in cs:
            if e in sub_graph_edges:
                intersect = True
                break
        if intersect:
            cross_sections_number += 1

    assert cross_sections_number - cross_sections_base_number >= 0
    uv_index = base_uv_index - 2 * (cross_sections_number - cross_sections_base_number)
    if uv_index < 0:
        return graph

    #
    # add stretching for divergent subgraph
    #
    stretcher_indices = set()
    for e in uv_sub_graph.externalEdges():
        for i, c in enumerate(e.flow.loop_momentas):
            if c != 0:
                stretcher_indices.add(i)
    assert len(stretcher_indices)
    stretcher_index = propagator.MomentumFlow.get_next_stretcher_index()

    for e in uv_sub_graph.internalEdges():
        stretchers_for_edges[RefEqualityWrapper(e)].append(propagator.Stretcher(frozenset(stretcher_indices), stretcher_index, uv_index))


class RefEqualityWrapper(object):
    def __init__(self, underlying):
        self.underlying = underlying

    def __hash__(self):
        return hash(self.underlying)

    def __eq__(self, other):
        assert isinstance(other, RefEqualityWrapper)
        return self.underlying is other.underlying
