#!/usr/bin/python
# -*- coding: utf8

from momentumrepr import graph_util_mr
import rggraphutil
import itertools
import graphine

__author__ = 'dima'


def find_edges_cross_sections(graph):
    for v in graph.vertices:
        if v != -1:
            assert v.tv_idx is not None
    time_version = sorted(graph.vertices - {graph.external_vertex}, key=lambda n: n.tv_idx)
    cross_section = list()
    for raw_sc in _iterate(time_version):
        sc_ = [x for x in _find_edges(graph, raw_sc[0], raw_sc[1])]
        cross_section.append(sc_)
    return cross_section


def assign_time_version(graph, time_version):
    node_map = dict()
    for tv_idx, node in enumerate(time_version):
        node_map[node] = node.copy(tv_idx=tv_idx)
    return graphine.Graph(map(lambda e: e.copy(node_map=node_map), graph))


def find_time_versions(graph):
    return sorted(map(lambda tv: assign_time_version(graph, tv), find_raw_time_versions(graph)))


def find_raw_time_versions(graph):
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
        for restriction in restrictions:
            if time_sequence.index(restriction[0]) < time_sequence.index(restriction[1]):
                return False
        return True

    time_versions = list()
    restrictions_ = find_restrictions(graph)
    for perm in itertools.permutations(graph.vertices - {graph.external_vertex}):
        if is_acceptable(restrictions_, perm):
            time_versions.append(perm)

    return time_versions


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