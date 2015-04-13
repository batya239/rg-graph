#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import uv
import graphine
import propagator
import time_versions
import graph_util_mr
import diff_util_mr
import propagator
import configure_mr
import map_reduce_wrapper
import integration
import momentum_enumeration
import integrations_merger
from rggraphutil import emptyListDict, zeroDict

no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible


BATCH = False


def kr1_log_divergence(graph_state_as_str, integration_operation=None):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, integration_operation=integration_operation)


def kr1_d_p2(graph_state_as_str, integration_operation=None):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, diff_util_mr.D_p2, integration_operation=integration_operation)


def kr1_d_iw(graph_state_as_str, integration_operation=None):
    return kr1_with_some_additional_lambda_operation(graph_state_as_str, diff_util_mr.D_i_omega, integration_operation=integration_operation)


def kr1_with_some_additional_lambda_operation(graph_state_as_str,
                                              additional_lambda=None,
                                              integration_operation=None):
    assert integration_operation is not None

    def integral_preparer_lambda(graph_with_tv):
        if configure_mr.Configure.debug():
            print "Graph: %s" % graph_with_tv.graph
            print "Time version: %s" % (graph_with_tv.time_version,)
        #TODO
        base_integrand, angles = integration.get_base_integrand_and_angles(graph_with_tv, additional_lambda == diff_util_mr.D_i_omega)
        # base_integrand, angles = integration.get_base_integrand_and_angles(graph_with_tv, False)
        loop_momentum_vars = integration.get_loop_momentum_vars(graph_with_tv)
        stretch_vars = integration.get_stretch_vars(graph_with_tv)
        return integrations_merger.IntegralRepresentation(base_integrand, loop_momentum_vars, angles, stretch_vars, graph_with_tv)

    def integral_producer_lambda(integral_representation, coeff):
        if configure_mr.Configure.debug():
            print "Coefficient:", coeff
            print "Graph Representator:", integral_representation.graph_representator
        return integration.construct_integrand(integral_representation.integrand,
                                               integral_representation.loop_momentas,
                                               integral_representation.stretchers,
                                               integral_representation.scalar_products, coeff)

    all_graph = graph_util_mr.from_str(graph_state_as_str)
    all_graph = map_reduce_wrapper.MapReduceAlgebraWrapper(all_graph)

    if configure_mr.Configure.do_d_tau():
        all_graph = all_graph.apply(diff_util_mr.D_minus_tau)

    BATCH = True

    answer_dict = zeroDict()
    for graph, c in all_graph.x_items():
        graph = map_reduce_wrapper.MapReduceAlgebraWrapper(graph)
        graph = graph.apply(momentum_enumeration.choose_minimal_momentum_flow)
        graph = graph.apply(propagator.subs_external_propagators_is_zero)
        graph = graph.apply(kr1_stretching)
        graph = graph.apply(integral_preparer_lambda)

        if BATCH:
            integrals = [integration.construct_integrand_batch(graph._mappings.items())]
        else:
            integrals = graph.map_with_coefficients(integral_producer_lambda)

        for i in integrals:
            integration_answer = integration_operation(*i)
            for d, a in integration_answer.items():
                answer_dict[d] += a * c.to_int()

    return answer_dict


def kr1_stretching(graph):
    uv_subgraphs = [x for x in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition)]
    graphs_and_time_versions = time_versions.find_time_versions(graph)

    with_stretching = list()
    for graph_and_tv in graphs_and_time_versions:
        stretchers_for_edges = emptyListDict()
        additional_regularizer = dict()
        g = graph_and_tv.graph
        uv_idx = 0
        for uv_graph in uv_subgraphs:
            add_stretching(g, uv_graph, graph_and_tv.edges_cross_sections, stretchers_for_edges, additional_regularizer, uv_idx)
            uv_idx += 1

        new_edges = list()
        for e in g.edges():
            stretchers = stretchers_for_edges[RefEqualityWrapper(e)]
            _e = e
            for s in stretchers:
                new_flow = _e.flow.stretch(s)
                _e = _e.copy(flow=new_flow)
            new_edges.append(_e)

        new_graph_with_stretching = graphine.Graph(new_edges, g.external_vertex)

        additional_regularizer = tuple(sorted(additional_regularizer.items(), key=lambda (k, v): k))
        with_stretching.append(graph_and_tv.set_graph(new_graph_with_stretching).set_regularizer(additional_regularizer))

    return with_stretching


def add_stretching(graph, uv_sub_graph, cross_sections, stretchers_for_edges, additional_regularizer, uv_idx):
    cross_sections_base_number = len(uv_sub_graph.vertices) - 2
    base_uv_index = uv.uv_index(uv_sub_graph)

    cross_sections_number = 0
    intersect_cross_sections = list()
    for cs in cross_sections:
        cross_sections_conj = list()
        intersect = False
        sub_graph_edges = set(uv_sub_graph.edges())
        for e in cs:
            if e in sub_graph_edges:
                intersect = True
            else:
                cross_sections_conj.append(e)
        if intersect:
            cross_sections_number += 1
            intersect_cross_sections.append(cross_sections_conj)

    assert cross_sections_number - cross_sections_base_number >= 0
    additional_regularizer_count = cross_sections_number - cross_sections_base_number
    # uv_index = base_uv_index - 2 * (cross_sections_number - cross_sections_base_number)
    uv_index = base_uv_index
    if uv_index < 0:
        return graph

    #
    # add stretching for divergent subgraph
    #
    stretcher_indices = set()
    for e in uv_sub_graph.external_edges:
        for i, c in enumerate(e.flow.loop_momentas):
            if c != 0:
                stretcher_indices.add(i)
    assert len(stretcher_indices)
    # stretcher_index = propagator.MomentumFlow.get_next_stretcher_index()
    stretcher_index = uv_idx
    assert stretcher_index not in additional_regularizer, str(additional_regularizer) + " " + str(stretcher_index)
    additional_regularizer[stretcher_index] = additional_regularizer_count

    for e in uv_sub_graph.internal_edges:
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