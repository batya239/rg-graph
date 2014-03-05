#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import itertools
import graph_util
import rggraphutil
import graphine
import momentum_enumeration
import scalar_product
import spherical_coordinats
import collections
from rggraphenv import symbolic_functions


def substitute_time_versions(graph):
    value = symbolic_functions.CLN_ZERO
    for cross_sections in find_edges_cross_sections(graph):
        v = symbolic_functions.CLN_ONE
        for cs in cross_sections:
            v /= reduce(lambda _v,  e: _v + e.propagator.energy_expression(), cs, symbolic_functions.CLN_ZERO)
        value += v
    return value


def substitute(graph_with_time_version):
    v = symbolic_functions.CLN_ONE
    for cs in graph_with_time_version.edges_cross_sections:
        v /= reduce(lambda _v,  e: _v + e.propagator.energy_expression(), cs, symbolic_functions.CLN_ZERO)
    return v


class GraphAndTimeVersion(object):
    def __init__(self, graph, time_version, edges_cross_sections=None):
        self._graph = graph
        self._time_version = time_version
        self._edges_cross_sections = edges_cross_sections

    @property
    def graph(self):
        return self._graph

    @property
    def time_version(self):
        return self._time_version

    @property
    def edges_cross_sections(self):
        if self._edges_cross_sections is None:
            self._edges_cross_sections = find_cross_sections_for_time_version(self.time_version, self.graph)
        return self._edges_cross_sections

    def set_graph(self, graph):
        return GraphAndTimeVersion(graph, self.time_version, self.edges_cross_sections)

    def __eq__(self, other):
        assert isinstance(other, GraphAndTimeVersion)
        return self.graph == other.graph and self.time_version == other.time_version

    def __hash__(self):
        return hash(self.graph) * 37 + hash(self.time_version)

    def __str__(self):
        return "graph=%s, time_version=%s" % (self.graph, self.time_version)

    __repr__ = __str__


def find_time_versions(graph):
    return map(lambda tv: GraphAndTimeVersion(graph, tv), find_raw_time_versions(graph))


def find_raw_time_versions(graph):
    def find_restrictions(g):
        restrictions = list()
        for e in g.allEdges():
            if e.fields == graph_util.Aa:
                restrictions.append(e.nodes)
            elif e.fields == graph_util.aA:
                restrictions.append(rggraphutil.swap_pair(e.nodes))
            elif not e.is_external():
                raise AssertionError()
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


def find_edges_cross_sections(graph):
    return map(lambda tv: find_cross_sections_for_time_version(time_version, graph), find_raw_time_versions(graph))


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


def main():
    graph = graphine.Graph(graph_util.from_str("e11|e|:00_Aa_Aa|00|:::"))
    graph = momentum_enumeration.attach_propagators(momentum_enumeration.choose_minimal_momentum_flow(graph))
    print graph
    print find_raw_time_versions(graph)
    print find_edges_cross_sections(graph)
    print substitute_time_versions(graph)
    graph = graphine.Graph(graph_util.from_str("e11|e|:00_Aa_aA|00|:::"))
    graph = momentum_enumeration.attach_propagators(momentum_enumeration.choose_minimal_momentum_flow(graph))
    print graph
    print find_raw_time_versions(graph)
    print find_edges_cross_sections(graph)
    print substitute_time_versions(graph)


if __name__ == "__main__":
    main()