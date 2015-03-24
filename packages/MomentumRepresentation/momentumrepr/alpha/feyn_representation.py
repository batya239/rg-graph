#!/usr/bin/python
# -*- coding: utf8
import time_versions
import graphine
import itertools
import uv
import configure_mr
import momentum_enumeration
from collections import namedtuple
from rggraphutil import emptyListDict, zeroDict
from cache import cached_function
from polynomial.multiindex import MultiIndex
from polynomial.polynomial import Polynomial

__author__ = 'dima'

AlphaRepresentationPolynomials = namedtuple("AlphaRepresentationPolynomials", ["c", "d"])
SubGraphInfo = namedtuple("SubGraphInfo", ["idx", "alpha_params", "loops_count", "edges", "divergence"])

no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible


class AlphaParameter(object):
    CURRENT_FEYNMAN_PARAMETER_IDX = -1

    def __init__(self, idx, letter="u"):
        self._idx = idx
        self._letter = letter

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

    def __hash__(self):
        return hash(self._idx) + 37 * hash(self._letter)

    def __cmp__(self, other):
        return cmp((self._letter, self._idx), (other._letter, other._idx))

    def __str__(self):
        return (self._letter + "%s") % self._idx

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
    result = graphine.Graph(new_edges)
    if configure_mr.Configure.debug():
        print "Graph:", result
    return result


@cached_function
def determine_conservation_laws(graph):
    assert graph.edges()[0].alpha_param is not None
    base_conservations = set()
    for v in graph.vertices:
        if v != graph.external_vertex:
            base_conservations.add(frozenset(map(lambda e: e.alpha_param, graph.edges(v))))
    base_conservations.discard(frozenset([graph.external_edges[0].alpha_param]))

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
    ret.discard(frozenset([graph.external_edges[0].alpha_param]))
    return ret


def find_sub_graphs_info(graph):
    uv_sub_graphs = [x for x in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition)]
    infos = list()

    edge_cs = time_versions.find_edges_cross_sections(graph)

    idx = 0
    for g in uv_sub_graphs:
        cross_sections_idx = 0
        for cs in edge_cs:
            for e in g:
                if e in cs:
                    cross_sections_idx += 1
                    break
        cross_sections_idx_base = len(g.vertices) - 2
        base_uv_index = uv.uv_index(g)
        assert cross_sections_idx_base <= cross_sections_idx, (
            "cross_sections_idx_base = %s, cross_sections_idx = %s, graph = %s" % (
                cross_sections_idx_base, cross_sections_idx, g))
        uv_index = base_uv_index - 2 * (cross_sections_idx - cross_sections_idx_base)
        if uv_index < 0:
            continue
        assert uv_index in (0, 2)

        sg_alpha_params = set()
        for e in g:
            if e.is_external():
                continue
            sg_alpha_params.add(e.alpha_param)
        assert len(sg_alpha_params)
        infos.append(SubGraphInfo(idx=idx,
                                  alpha_params=sg_alpha_params,
                                  loops_count=g.loops_count,
                                  edges=g,
                                  divergence=uv_index))
        idx += 1
    return graph, infos


def cross_sections_substitutions(graph, sub_graph_infos):
    graph = momentum_enumeration.choose_momentum_flow(graph)
    edge_cs = time_versions.find_edges_cross_sections(graph)
    index = 0
    v_params = set()
    raw_substitutors = emptyListDict()

    flow_to_index = dict()
    index_rate = zeroDict()

    for cs in edge_cs:
        cs_flow = frozenset(map(lambda e: frozenset([e.flow, -e.flow]), cs))
        if cs_flow in flow_to_index:
            index = flow_to_index[cs_flow]
        else:
            flow_to_index[cs_flow] = index
        index_rate[index] += 1
        cs_alpha_params = set(map(lambda e: e.alpha_param, cs))
        stretch_multipliers = emptyListDict()
        for sg_info in sub_graph_infos:
            co_sub_graph_alphas = set(cs_alpha_params) - set(sg_info.alpha_params)
            if len(co_sub_graph_alphas) != len(cs_alpha_params):
                for param in co_sub_graph_alphas:
                    stretch_multipliers[param].append(sg_info.idx)
        for u in cs_alpha_params:
            raw_substitutors[u].append((index, stretch_multipliers.get(u, tuple())))
        index = max(index_rate.keys()) + 1
    substitutors = dict()
    for k, raw_subs in raw_substitutors.iteritems():
        raw_polynomial = zeroDict()
        for v_idx, stretcher in raw_subs:
            v_param = AlphaParameter(v_idx, letter="v")
            v_params.add(v_param)

            raw_multi_index = {v_param: 1}
            for a in stretcher:
                raw_multi_index[AlphaParameter(a, "a")] = 1
            raw_polynomial[MultiIndex(raw_multi_index)] += 1
        substitutors[k] = Polynomial(raw_polynomial)
    index_rate = dict(map(lambda (k, v): (AlphaParameter(k, letter="v"), v), index_rate.iteritems()))
    return substitutors, tuple(v_params), index_rate


def construct_monomial(alpha_params, sub_graphs_info):
    raw_result = dict()
    for sg_info in sub_graphs_info:
        idx = sg_info.idx
        deg = len(alpha_params & sg_info.alpha_params) - sg_info.loops_count
        if deg > 0:
            stretch_var = AlphaParameter(idx, "a")
            assert stretch_var not in raw_result
            raw_result[stretch_var] = deg
    for alpha_param in alpha_params:
        raw_result[alpha_param] = 1
    return MultiIndex(raw_result)


def construct_feyn_repr_polynomials(graph, sub_graphs_info):
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
        assert len(comb) == graph.loops_count + 1
        determinant.add(comb)

    determinant = set(map(lambda m: construct_monomial(m, sub_graphs_info), determinant))

    u_external_vertex = graph.external_edges[0].alpha_param
    u_external_var = u_external_vertex

    def remove_u_external(m):
        return m - MultiIndex({u_external_var: 1})

    determinant_c = filter(lambda m: m.getVarPower(u_external_var) == 0, determinant)
    determinant_d = map(lambda m: remove_u_external(m),
                        filter(lambda m: m.getVarPower(u_external_var) != 0, determinant))

    raw_poly_c = dict()
    for m in determinant_c:
        assert m not in raw_poly_c
        raw_poly_c[m] = 1
    determinant_c = Polynomial(raw_poly_c)

    raw_poly_d = dict()
    for m in determinant_d:
        assert m not in raw_poly_d
        raw_poly_d[m] = 1
    determinant_d = Polynomial(raw_poly_d)

    return AlphaRepresentationPolynomials(c=determinant_c, d=determinant_d)


def get_polynomials(graph):
    graph = introduce_feynman_parameters(graph)
    graph, sub_graph_infos = find_sub_graphs_info(graph)
    c, d = construct_feyn_repr_polynomials(graph, sub_graph_infos)
    c_tau = tau_factor(graph)
    c_omega = minus_i_omega_factor(graph)
    substitutor, v_params, v_power = cross_sections_substitutions(graph, sub_graph_infos)
    if configure_mr.Configure.debug():
        print "C:", c
        print "D:", d
        print "C_tau:", c_tau
        print "C_omega:", c_omega
        print "Time version substitutors:", substitutor
    return c, d, c_tau, c_omega, substitutor, v_params, v_power, graph


def minus_i_omega_factor(graph):
    shortest_flow_path = graphine.util.find_shortest_momentum_flow(graph)
    return tuple(map(lambda (e, sign): e.alpha_param, shortest_flow_path))


def tau_factor(graph):
    return tuple(map(lambda e: e.alpha_param, filter(lambda e: not e.is_external(), graph)))