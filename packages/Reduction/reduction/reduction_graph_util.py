__author__ = 'dima'


import graph_state
import graphine


CONFIG = graph_state.PropertiesConfig.create(graph_state.PropertyKey(name="weight",
                                                                     is_directed=False,
                                                                     externalizer=graph_state.PropertyExternalizer()))

graph_from_str = lambda s: graphine.Graph.from_str(s, CONFIG)
new_edge = CONFIG.new_edge
