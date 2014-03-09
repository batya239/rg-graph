#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import graph_state
import propagator
import graphine


MAIN_GRAPH_CONFIG = graph_state.PropertiesConfig.create(graph_state.PropertyKey(name="fields",
                                                                                is_directed=True,
                                                                                externalizer=graph_state.Fields.externalizer()),
                                                        graph_state.PropertyKey(name="flow",
                                                                                is_directed=False,
                                                                                externalizer=graph_state.PropertyExternalizer()),
                                                        graph_state.PropertyKey(name="propagator",
                                                                                is_directed=False,
                                                                                externalizer=graph_state.PropertyExternalizer()),
                                                        graph_state.PropertyKey(name="arrow",
                                                                                is_directed=True,
                                                                                externalizer=graph_state.Arrow.Externalizer()),
                                                        graph_state.PropertyKey(name="marker",
                                                                                is_directed=False,
                                                                                externalizer=graph_state.PropertyExternalizer()))


new_edge = MAIN_GRAPH_CONFIG.new_edge


def from_str(graph_state_str):
    return graphine.Graph.fromStr(graph_state_str, MAIN_GRAPH_CONFIG)


aa = graph_state.Fields("aa")
Aa = graph_state.Fields("Aa")
aA = - Aa

MARKER_0 = "0"
MARKER_1 = "1"