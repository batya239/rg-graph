#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graphine
import itertools
import uv
from collections import namedtuple
from rggraphenv import symbolic_functions
from cache import cached_function

AlphaRepresentationPolynomials = namedtuple("AlphaRepresentationPolynomials", ["c", "d"])
SubGraphInfo = namedtuple("SubGraphInfo", ["idx", "alpha_params", "loops_count", "internal_momentum_idxs", "edges"])

no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible


class AlphaParameter(object):
    CURRENT_FEYNMAN_PARAMETER_IDX = -1

    def __init__(self, idx):
        self._idx = idx

    @staticmethod
    def reset():
        AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX = -1

    @staticmethod
    def next():
        AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX += 1
        return AlphaParameter(AlphaParameter.CURRENT_FEYNMAN_PARAMETER_IDX)

    @staticmethod
    def external():
        return AlphaParameter(0)

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
    AlphaParameter.reset()
    new_edges = list()
    external_alpha_param = AlphaParameter.next()
    for e in graph.external_edges:
        new_edges.append(e.copy(alpha_param=external_alpha_param))
    new_edges += map(lambda e: e.copy(alpha_param=AlphaParameter.next()), graph.internal_edges)
    return graphine.Graph(new_edges)


@cached_function
def build_determinants_tilde_static(graph):
    assert graph.edges()[0].alpha_param is not None
    laws = determine_conservation_laws(graph)
    alpha_params = list(set(map(lambda e: e.alpha_param, graph)))

    determinant = set()
    for comb in itertools.combinations(alpha_params, graph.loops_count + 1):
        comb = frozenset(comb)
        do_continue = False
        for l in laws:
            if l.issubset(comb):
                do_continue = True
                break
        if do_continue:
            continue
        determinant.add(comb)

    u0 = AlphaParameter.external()
    d = filter(lambda m: u0 in m, determinant)
    d = map(lambda m: sorted(list(m - {u0})), d)

    c = filter(lambda m: AlphaParameter.external() not in m, determinant)
    return AlphaRepresentationPolynomials(c=c, d=d)


@cached_function
def determine_conservation_laws(graph):
    assert graph.edges()[0].alpha_param is not None
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
            conversation = frozenset(curr)
            if len(conversation) <= graph.loops_count + 1:
                ret.add(conversation)
    ret.discard(frozenset([]))
    return ret


def find_sub_graphs_info(graph):
    uv_sub_graphs = [x for x in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition)]
    infos = list()

    idx = 0
    for g in uv_sub_graphs:
        co_sg_internal_momenta = set()
        for e in graph:
            if e not in g:
                for idx, c in enumerate(e.loop_momentas()):
                    if c != 0:
                        co_sg_internal_momenta.add(idx)

        sg_alpha_params = set()
        for e in g:
            if e.is_external:
                continue
            sg_alpha_params.add(e.alpha_param)
        infos.append(SubGraphInfo(idx=idx,
                                  alpha_params=sg_alpha_params,
                                  loops_count=g.loops_count,
                                  internal_momentum_idxs=set([x for x in xrange(graph.loops_count)]) - co_sg_internal_momenta,
                                  edges=g))
        idx += 1

    return graph, infos


class Monomial(object):
    def __init__(self, alpha_params, stretchers):
        self.alpha_params = list(frozenset(alpha_params))
        self.stretchers = tuple(stretchers)

    def __eq__(self, other):
        return self.alpha_params == other.alpha_params and self.stretchers == other.stretchers

    def __hash__(self):
        return hash(self.alpha_params) + 37 * hash(self.stretchers)

    def contains_alpha_param(self, alpha_param):
        return alpha_param in self.alpha_params

    def remove_alpha_param(self, alpha_param):
        return Monomial(alpha_param.difference([alpha_param]), self.stretchers)

    @staticmethod
    def construct(alpha_params, sub_graphs_info):
        stretch_indices = list()
        for idx, sg_info in sub_graphs_info:
            deg = len(alpha_params & sub_graphs_info.alpha_params) - sub_graphs_info.loops_count
            if deg > 0:
                assert idx not in stretch_indices
                stretch_indices += [idx] * deg
        return Monomial(alpha_params, stretch_indices)


def construct_alpha_repr_polynomials(graph, sub_graphs_info):
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

    determinant = set(map(lambda m: Monomial.construct(m, sub_graphs_info), determinant))

    u_external_vertex = graph.external_edges[0].alpha_param
    determinant_c = filter(lambda m: m.contains_alpha_param(u_external_vertex), determinant)
    determinant_d = map(lambda m: m.remove_alpha_param(u_external_vertex), filter(lambda m: u_external_vertex in m, determinant))
    return AlphaRepresentationPolynomials(c=determinant_c, d=determinant_d)


class DeltaFunction(object):
    Entry = namedtuple("Entry", ["c", "alpha_param", "stretchers"])

    def __init__(self, entries):
        self.entries = entries


def find_delta_functions(graph, sub_graphs_info):
    deltas = list()
    for idx in xrange(graph.loops_count):
        entries = list()
        for e in graph:
            c = e.flow.loop_momentas[idx]
            if c == 0:
                continue
            stretch_idxs = list()
            for sg_info in sub_graphs_info:
                sg_edges = sg_info.edges
                if e in sg_edges and idx in sg_info.internal_momentum_idxs:
                    stretch_idxs.append(sg_info.idx)
            entries.append(DeltaFunction.Entry(c=c, alpha_param=e.alpha_param, stretchers=stretch_idxs))
        deltas.append(DeltaFunction(entries))
    return deltas


def find_frequency_exponent_param(graph, sub_graphs_info):
    entries = list()
    for e in graph:
        assert len(e.flow.loop_momentas) == 1
        c = e.flow.loop_momentas[0]
        if c == 0:
            continue
        stretch_idxs = list()
        for sg_info in sub_graphs_info:
            if e in sg_info.edges:
                stretch_idxs.append(sg_info.idx)
        entries.append(DeltaFunction.Entry(c=c, alpha_param=e.alpha_param, stretchers=stretch_idxs))
    return DeltaFunction(entries)