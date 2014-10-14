#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

from graph_state import PropertiesConfig, GraphState, graph_state_property, Rainbow


class Externalizer(graph_state_property.PropertyExternalizer):
    def deserialize(self, string):
        try:
            return int(string)
        except:
            return string



gs_builder = PropertiesConfig.create(graph_state_property.PropertyKey(name="colors",
                                                                      is_directed=False,
                                                                      externalizer=graph_state_property.PropertyExternalizer()),
                                     graph_state_property.PropertyKey(name='n_num',
                                                                      is_directed=False,
                                                                      is_edge_property=False,
                                                                      externalizer=Externalizer()))


gs_builder.GraphState = GraphState