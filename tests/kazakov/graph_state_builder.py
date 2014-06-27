#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

from graph_state import PropertiesConfig, GraphState, PropertyExternalizer, PropertyKey, graph_state_property

gs_builder = PropertiesConfig.create(graph_state_property.PropertyKey(name='e_num',
                                                                         is_directed=False,
                                                                         is_edge_property=True,
                                                                         externalizer=graph_state_property.PropertyExternalizer()))

# gs_builder = PropertiesConfig.create(graph_state_property.PropertyKey(name='e_num',
#                                                                          is_directed=False,
#                                                                          is_edge_property=True,
#                                                                          externalizer=graph_state_property.PropertyExternalizer()),
#                                  graph_state_property.PropertyKey(name='n_num',
#                                                                          is_directed=False,
#                                                                          is_edge_property=False,
#                                                                          externalizer=graph_state_property.PropertyExternalizer()))



