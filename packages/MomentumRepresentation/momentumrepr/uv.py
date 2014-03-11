#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import configure_mr
import graphine


@graphine.filters.graphFilter
def uv_condition(edgesList, superGraph, superGraphEdges):
    g = graphine.Graph(edgesList, superGraph.external_vertex)
    return uv_index(g) >= 0


def uv_index(graph):
    _uv_index = - graph.getAllInternalEdgesCount() * 2 \
                + numerators_count(graph) \
                + graph.getLoopsCount() * (2 + configure_mr.Configure.space_dimension_int())
    return _uv_index


def numerators_count(graph):
    cnt = 0
    for e in graph.allEdges():
        if e.arrow is not None and not e.arrow.is_null():
            cnt += 1
    return cnt