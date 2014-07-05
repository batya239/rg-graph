#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

from graph_state import PropertiesConfig, GraphState, graph_state_property, Rainbow

gs_builder = PropertiesConfig.create(graph_state_property.PropertyKey(name="colors",
                                                                      is_directed=False,
                                                                      externalizer=Rainbow.Externalizer()))

