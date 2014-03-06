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
    _uv_index = - graph.getAllInternalEdgesCount() * 2 + graph.getLoopsCount() * (2 + configure_mr.Configure.space_dimension_int())
    return _uv_index