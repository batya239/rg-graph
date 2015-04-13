#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import itertools
import graph_util_mr
import rggraphutil
import graphine
import momentum_enumeration
import scalar_product
import spherical_coordinats
import collections
import scalar_product
import spherical_coordinats
from rggraphenv import symbolic_functions


def substitute(graph_with_time_version, d_iw=False):
    _scalar_product = scalar_product.extract_scalar_products(graph_with_time_version.graph)

    sps = set() if _scalar_product is None else _scalar_product.momentum_pairs()
    sps = reduce(lambda s, e: s | e.flow.get_raw_scalar_products(), graph_with_time_version.graph.edges(), sps)

    substitutor = spherical_coordinats.ScalarProductEnumerator.enumerate(sps, graph_with_time_version.graph.loops_count)

    v = symbolic_functions.CLN_ONE
    for cs in graph_with_time_version.edges_cross_sections:
        indices = reduce(lambda s, e: s | e.flow.get_not_all_propagators_stretchers_indices(), cs, set())
        v /= reduce(lambda _v,  e: _v + e.flow.energy_expression(indices, substitutor), cs, symbolic_functions.CLN_ZERO)

    if _scalar_product is not None:
        v *= _scalar_product.substitute(substitutor)

    assert graph_with_time_version.additional_regulizer is not None
    reg = symbolic_functions.CLN_ONE
    for (idx, c) in graph_with_time_version.additional_regulizer:
        reg *= symbolic_functions.var("a%s" % idx) ** symbolic_functions.cln(c)
    v *= reg ** symbolic_functions.CLN_TWO

    if d_iw:
        iw_tv = symbolic_functions.CLN_ZERO
        for cs in graph_with_time_version.edges_cross_sections:
            c = symbolic_functions.CLN_ONE
            indices = reduce(lambda s, e: s | e.flow.get_not_all_propagators_stretchers_indices(), cs, set())
            for _v in indices:
                c *= symbolic_functions.var("a%s" % _v) ** symbolic_functions.CLN_TWO
            iw_tv += c / reduce(lambda _v,  e: _v + e.flow.energy_expression(indices, substitutor), cs, symbolic_functions.CLN_ZERO)
        print v
        v *= iw_tv

    return v, substitutor.values()


class GraphAndTimeVersion(object):
    def __init__(self, graph, time_version, additional_regularizer=None):
        self._graph = graph
        self._time_version = time_version
        self._additional_regularizer = additional_regularizer

    @property
    def graph(self):
        return self._graph

    @property
    def time_version(self):
        return self._time_version

    @property
    def additional_regulizer(self):
        return self._additional_regularizer

    @property
    def edges_cross_sections(self):
        return find_cross_sections_for_time_version(self.time_version, self.graph)

    def set_graph(self, graph):
        return GraphAndTimeVersion(graph, self.time_version, self.additional_regulizer)

    def set_regularizer(self, additional_regularizer):
        return GraphAndTimeVersion(self.graph, self.time_version, additional_regularizer)

    def __eq__(self, other):
        assert isinstance(other, GraphAndTimeVersion)
        return self.graph == other.graph and self.time_version == other.time_version and self.additional_regulizer == other.additional_regulizer

    def __hash__(self):
        return (37 * hash(self.additional_regulizer) + hash(self.graph)) * 37 + hash(self.time_version)

    def __str__(self):
        return "graph=%s, time_version=%s, additional_regularizer=%s" % (self.graph, self.time_version, self.additional_regulizer)

    __repr__ = __str__


def find_constraints(graph):
    order = list()
    for v in graph.vertices:
        if v.tv_idx is not None:
            assert v not in order
            order.append(v)
    if not len(order):
        return tuple()
    return sorted(order, key=lambda v: v.tv_idx)


def find_time_versions(graph):
    constraints = find_constraints(graph)
    return sorted(map(lambda tv: GraphAndTimeVersion(graph, tv), find_raw_time_versions(graph, constraints)))


def find_raw_time_versions(graph, constraints):
    def find_restrictions(g):
        restrictions = list()
        for e in g:
            if e.fields == graph_util_mr.Aa:
                restrictions.append(e.nodes)
            elif e.fields == graph_util_mr.aA:
                restrictions.append(rggraphutil.swap_pair(e.nodes))
            elif not e.is_external():
                raise AssertionError(e)
        return restrictions

    def is_acceptable(restrictions, time_sequence):
        if len(constraints):
            constraint_indices = filter(lambda i: i is not None, map(lambda v: None if v not in constraints else constraints.index(v), time_sequence))
            if constraint_indices != sorted(constraint_indices):
                return False
        for restriction in restrictions:
            if time_sequence.index(restriction[0]) < time_sequence.index(restriction[1]):
                return False
        return True

    time_versions = list()
    restrictions = find_restrictions(graph)
    for perm in itertools.permutations(graph.vertices - set([graph.external_vertex])):
        if is_acceptable(restrictions, perm):
            time_versions.append(perm)

    return time_versions


def find_cross_sections_for_time_version(time_version, graph):
    cross_section = list()
    for raw_sc in _iterate(time_version):
        sc_ = [x for x in _find_edges(graph, raw_sc[0], raw_sc[1])]
        cross_section.append(sc_)
    return cross_section


def _iterate(time_version):
    for i, v in enumerate(time_version):
        if i != 0:
            yield set(time_version[:i]), set(time_version[i:])


def _find_edges(graph, from_set, to_set):
    for v in from_set:
        for e in graph.edges(v):
            for _v in e.nodes:
                if _v != v and _v in to_set:
                    yield e