#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import graph_state
import graphine



class StringPropertyExternalizer(graph_state.PropertyExternalizer):
    def deserialize(self, string):
        return string

    def serialize(self, obj):
        return obj


MS_GRAPH_CONFIG = graph_state.PropertiesConfig.create(graph_state.PropertyKey(name="fields",
                                                                              is_directed=True,
                                                                              externalizer=graph_state.Fields.externalizer()),
                                                      graph_state.PropertyKey(name="flow",
                                                                              is_directed=True,
                                                                              externalizer=graph_state.PropertyExternalizer()),
                                                      graph_state.PropertyKey(name="alpha_param",
                                                                              is_directed=False,
                                                                              externalizer=graph_state.PropertyExternalizer()),
                                                      graph_state.PropertyKey(name="tv_idx",
                                                                              is_edge_property=False,
                                                                              externalizer=graph_state.PropertyExternalizer()),
                                                      graph_state.PropertyKey(name="factor", is_edge_property=False,
                                                                              externalizer=StringPropertyExternalizer()))


def from_str(gs):
    return graphine.Graph(MS_GRAPH_CONFIG.graph_state_from_str(gs))

new_edge = MS_GRAPH_CONFIG.new_edge