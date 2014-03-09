#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import uv
import graphine
import propagator
import time_versions
import graph_util_mr
import diff_util_mr
import representation
import propagator
import configure_mr
import map_reduce_wrapper
import integration
from rggraphutil import emptyListDict, zeroDict

no_tadpoles = graphine.filters.noTadpoles
one_irreducible = graphine.filters.oneIrreducible


def kr1_log_divergence(graph_state_as_str, integration_operation=None):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, integration_operation=integration_operation)


def kr1_d_p2(graph_state_as_str, integration_operation=None):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, diff_util_mr.D_p2, integration_operation=integration_operation)


def kr1_d_iw(graph_state_as_str, integration_operation=None):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, diff_util_mr.D_i_omega, integration_operation=integration_operation)


def kr1_with_some_additional_lambda_operation(graph_state_as_str,
                                              additional_lambda=None,
                                              integration_operation=None):
    def integral_producer_lambda(graph_with_tv, coeff):
        if configure_mr.Configure.debug():
            print "\n\n\nGraph: %s" % graph_with_tv.graph
            print "Coefficient:", coeff
            print "Time version: %s" % (graph_with_tv.time_version,)
        base_integrand, angles = integration.get_base_integrand_and_angles(graph_with_tv)
        # base_integrand *= coeff
        loop_momentum_vars = integration.get_loop_momentum_vars(graph_with_tv)
        stretch_vars = integration.get_stretch_vars(graph_with_tv)
        # angles = integration.get_angles(graph_with_tv)
        return integration.construct_integrand(base_integrand, loop_momentum_vars, stretch_vars, angles, coeff)

    graph = graph_util_mr.from_str(graph_state_as_str)
    graph = map_reduce_wrapper.MapReduceAlgebraWrapper(graph)
    graph = graph.apply(diff_util_mr.D_minus_tau)
    if additional_lambda is not None:
        graph = graph.apply(additional_lambda)
    graph = graph.apply(representation.enumerate_propagators)
    graph = graph.apply(propagator.subs_external_propagators_is_zero)
    graph = graph.apply(kr1_stretching)
    integrals = graph.map_with_coefficients(integral_producer_lambda)

    if integration_operation is None:
        return integrals

    answer_dict = zeroDict()
    for i in integrals:
        for d, a in integration_operation(*i).items():
            answer_dict[d] += a
            print "Current answer[%s]: %s, delta %s" % (d, answer_dict[d], a)
    return answer_dict


def kr1_stretching(graph):
    uv_subgraphs = [x for x in graph.xRelevantSubGraphs(one_irreducible + no_tadpoles + uv.uv_condition)]
    graphs_and_time_versions = time_versions.find_time_versions(graph)

    print "Graph:", graph
    for g_tv in graphs_and_time_versions:
        print "Time version:", g_tv.time_version

    with_stretching = list()
    for graph_and_tv in graphs_and_time_versions:
        stretchers_for_edges = emptyListDict()
        g = graph_and_tv.graph
        for uv_graph in uv_subgraphs:
            add_stretching(g, uv_graph, graph_and_tv.edges_cross_sections, stretchers_for_edges)

        new_edges = list()
        for e in g.allEdges():
            stretchers = stretchers_for_edges[RefEqualityWrapper(e)]
            _e = e
            for s in stretchers:
                new_flow = _e.flow.stretch(s)
                _e = _e.copy(flow=new_flow, propagator=propagator.StandartPropagator(new_flow, True))
            new_edges.append(_e)

        new_graph_with_stretching = graphine.Graph(new_edges, g.external_vertex)


        print "New graph with stretching:", new_graph_with_stretching
        print "Stretchers for edges", stretchers_for_edges
        with_stretching.append(graph_and_tv.set_graph(new_graph_with_stretching))

    print "\n"

    return with_stretching


def add_stretching(graph, uv_sub_graph, cross_sections, stretchers_for_edges):
    cross_sections_base_number = len(uv_sub_graph.vertices()) - 2
    base_uv_index = uv.uv_index(uv_sub_graph)

    cross_sections_number = 0
    intersect_cross_sections = list()
    for cs in cross_sections:
        cross_sections_conj = list()
        intersect = False
        sub_graph_edges = set(uv_sub_graph.allEdges())
        for e in cs:
            if e in sub_graph_edges:
                intersect = True
            else:
                cross_sections_conj.append(e)
        if intersect:
            cross_sections_number += 1
            intersect_cross_sections.append(cross_sections_conj)

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
        stretchers_for_edges[RefEqualityWrapper(e)].append(propagator.Stretcher(False, frozenset(stretcher_indices), stretcher_index, uv_index))

    for conj in intersect_cross_sections:
        for e in conj:
            stretchers_for_edges[RefEqualityWrapper(e)].append(propagator.Stretcher(True, None, stretcher_index, uv_index))


class RefEqualityWrapper(object):
    def __init__(self, underlying):
        self.underlying = underlying

    def __hash__(self):
        return hash(self.underlying)

    def __eq__(self, other):
        assert isinstance(other, RefEqualityWrapper)
        return self.underlying is other.underlying

    def __str__(self):
        return str(self.underlying)