#!/usr/bin/python
# -*- coding: utf8 -*-

__author__ = 'dima'


class Externalizer(object):
    def read_graph_state(self, string):
        pass

    def write_graph_state(self, graph_state):
        prop_config = graph_state._properties_config

# self._property_order = property_order
#         self._property_directionality = property_directionality
#         self._property_externalizer = property_externalizer
#         self._property_target = property_target
# property_order = [None] * len(property_keys)
#         property_directionality = dict()
#         property_externalizer = dict()
#         property_target = dict()
#         for i, k in enumerate(property_keys):
#             property_order[i] = k.name
#             property_directionality[k.name] = k.is_directed
#             property_externalizer[k.name] = k.externalizer
#             property_target[k.name] = k.is_edge_property

        edge_prop_count = prop_config._property_target.values().count(True)
        vertex_prop_count = prop_config._property_target.values().count(False)
        if edge_prop_count > 1 or vertex_prop_count > 1:
            raise AssertionError("Can't export complex GraphState (can convert only single edge property and single vertex property)")

        edge_prop_idx = None
        if edge_prop_count > 0:
            for k, v in prop_config._property_target.iteritems():
                if v:
                    edge_prop_idx = k
                    break

        vertex_prop_idx = None
        if vertex_prop_count > 0:
            for k, v in prop_config._property_target.iteritems():
                if not v:
                    vertex_prop_idx = k
                    break

        is_directed = False if edge_prop_idx is None else prop_config._property_directionality[vertex_prop_idx]

        def edge_property_extractor(e):
            return None if edge_prop_idx is None else e.getitem(edge_prop_idx)

        def vertex_property_extractor(v):
            return None if vertex_prop_idx is None else e.getitem(vertex_prop_idx)

        for e in graph_state:
            pass
