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


def substitute(graph_with_time_version):
    _scalar_product = scalar_product.extract_scalar_products(graph_with_time_version.graph)

    sps = set() if _scalar_product is None else _scalar_product.momentum_pairs()
    sps = reduce(lambda s, e: s | e.flow.get_raw_scalar_products(), graph_with_time_version.graph.allEdges(), sps)

    substitutor = spherical_coordinats.ScalarProductEnumerator.enumerate(sps, graph_with_time_version.graph.getLoopsCount())

    v = symbolic_functions.CLN_ONE
    for cs in graph_with_time_version.edges_cross_sections:
        indices = reduce(lambda s, e: s | e.flow.get_not_all_propagators_stretchers_indices(), cs, set())
        v /= reduce(lambda _v,  e: _v + e.flow.energy_expression(indices, substitutor), cs, symbolic_functions.CLN_ZERO)

    if _scalar_product is not None:
        v *= _scalar_product.substitute(substitutor)

    return v, substitutor.values()


class GraphAndTimeVersion(object):
    def __init__(self, graph, time_version):
        self._graph = graph
        self._time_version = time_version

    @property
    def graph(self):
        return self._graph

    @property
    def time_version(self):
        return self._time_version

    @property
    def edges_cross_sections(self):
        return find_cross_sections_for_time_version(self.time_version, self.graph)

    def set_graph(self, graph):
        return GraphAndTimeVersion(graph, self.time_version)

    def __eq__(self, other):
        assert isinstance(other, GraphAndTimeVersion)
        return self.graph == other.graph and self.time_version == other.time_version

    def __hash__(self):
        return hash(self.graph) * 37 + hash(self.time_version)

    def __str__(self):
        return "graph=%s, time_version=%s" % (self.graph, self.time_version)

    __repr__ = __str__


def find_time_versions(graph):
    return sorted(map(lambda tv: GraphAndTimeVersion(graph, tv), find_raw_time_versions(graph)))


def find_raw_time_versions(graph):
    def find_restrictions(g):
        restrictions = list()
        for e in g.allEdges():
            if e.fields == graph_util_mr.Aa:
                restrictions.append(e.nodes)
            elif e.fields == graph_util_mr.aA:
                restrictions.append(rggraphutil.swap_pair(e.nodes))
            elif not e.is_external():
                raise AssertionError(e)
        return restrictions

    def is_acceptable(restrictions, time_sequence):
        for restriction in restrictions:
            if time_sequence.index(restriction[0]) < time_sequence.index(restriction[1]):
                return False
        return True

    time_versions = list()
    restrictions = find_restrictions(graph)
    for perm in itertools.permutations(graph.vertices() - set([graph.external_vertex])):
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