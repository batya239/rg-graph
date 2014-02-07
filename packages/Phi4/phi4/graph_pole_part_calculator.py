#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graphine
import r
import common
from rggraphenv import symbolic_functions


def calculate_graph_pole_part(graph,
                              k_operation=common.MS_K_OPERATION,
                              uv_filter=common.DEFAULT_SUBGRAPH_UV_FILTER,
                              description="graph pole part calculator",
                              use_graph_calculator=True):
    """
    calculates some inversion of KR*
    """
    assert graph.externalEdgesCount() == 2
    tadpole = graph.deleteEdges(graph.externalEdges())
    kr_star = r.KRStar(tadpole,
                       k_operation,
                       uv_filter,
                       description=description,
                       use_graph_calculator=use_graph_calculator)
    co_part = r.KRStar(graph,
                       k_operation,
                       uv_filter,
                       description=description,
                       use_graph_calculator=use_graph_calculator,
                       minus_graph=True)
    return kr_star - co_part + symbolic_functions.Order(1)