#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graphine
import itertools
from collections import namedtuple
from rggraphenv import symbolic_functions
from rggraphutil import emptyListDict


AlphaRepresentationPolynomials = namedtuple("AlphaRepresentationPolynomials", ["c", "d"])


class AlphaParameter(object):
    CURRENT_FEYNMAN_PARAMETER_IDX = -1

    def __init__(self, idx):
        self._idx = idx

    @staticmethod
    def next():
        AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX += 1
        return AlphaParameter(AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX)

    def as_var(self):
        return symbolic_functions.var(str(self))

    def __hash__(self):
        return self._idx

    def __cmp__(self, other):
        return cmp(self._idx, other._idx)

    def __str__(self):
        return "u%s" % self._idx

    __repr__ = __str__


class AlphaParameterIdentityWrapper(object):
    def __init__(self, flow):
        self._flow = flow

    @property
    def flow(self):
        return self._flow

    def __hash__(self):
        return 0

    def __eq__(self, other):
        s_flow = self.flow
        o_flow = other.flow
        return s_flow - o_flow == 0 or s_flow + o_flow == 0


def introduce_feynman_parameters(graph):
    assert graph.edges()[0].flow is not None
    flow_to_edge = emptyListDict()
    for e in graph:
        flow_to_edge[AlphaParameterIdentityWrapper(e.flow)].append(e)

    modified_edges = list()
    for similar_edges in flow_to_edge.values():
        alpha_param = AlphaParameter.next()
        for e in similar_edges:
            modified_edges.append(e.copy(alpha_param=alpha_param))

    assert len(modified_edges) == len(graph)
    return graphine.Graph(modified_edges)


def determine_conservation_laws(graph):
    assert graph.edges()[0].alpha_param is not None
    print graph
    base_conservations = set()
    for v in graph.vertices:
        if v != graph.external_vertex:
            base_conservations.add(frozenset(map(lambda e: e.alpha_param, graph.edges(v))))

    ret = set()
    for n in range(1, len(base_conservations) + 1):
        for combination in itertools.combinations(base_conservations, n):
            curr = set()
            for s in combination:
                curr.symmetric_difference_update(s)
            ret.add(frozenset(curr))
    ret.discard(frozenset([]))
    return ret


def construct_alpha_repr_polynomials(graph):
    assert graph.edges()[0].alpha_param is not None
    laws = determine_conservation_laws(graph)
    all_alpha_params = set(map(lambda e: e.alpha_param, graph))

    determinant = set()
    for comb in itertools.combinations(all_alpha_params, graph.loops_count + 1):
        comb = frozenset(comb)
        do_continue = False
        for l in laws:
            if l.issubset(comb):
                do_continue = True
                break
        if do_continue:
            continue
        determinant.add(comb)

    u_external_vertex = graph.external_edges[0].alpha_param
    determinant_d = filter(lambda m: u_external_vertex not in m, determinant)
    determinant_c = map(lambda m: m.difference([u_external_vertex]), filter(lambda m: u_external_vertex in m, determinant))
    return AlphaRepresentationPolynomials(c=determinant_c, d=determinant_d)


# import graph_util_mr
# import configure_mr
# import momentum_enumeration
# configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.e).with_target_loops_count(3).\
#     with_maximum_points_number("50000000000LL").\
#     with_absolute_error(10e-10).\
#     with_relative_error(10e-8).\
#     with_integration_algorithm("vegas").\
#     with_debug(True).configure()
# g = graph_util_mr.from_str_alpha("e12|e3|33||:0A_aA_aA|0a_Aa|aA_aA||::::")
# g = momentum_enumeration.choose_minimal_momentum_flow(g)
# g = introduce_feynman_parameters(g)
# ps = construct_alpha_repr_polynomials(g)
# print ps.c
# print ps.d