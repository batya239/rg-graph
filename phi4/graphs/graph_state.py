#!/usr/bin/python
# -*- coding: utf8 -*-

import copy
import itertools
import nickel


class Fields(object):
    A = 0
    B = 1
    EXTERNAL = 3

    def __init__(self, pair):
      self._pair = pair[0], pair[1]

    @property
    def pair(self):
        return self._pair

    def __cmp__(self, other):
      return cmp(self.pair, other.pair)

    def copy(self, swap=False):
        if swap:
          return Fields(tuple(reversed(self.pair)))
        return Fields(self.pair)

    def __str__(self):
      return hex(self.pair[0] * 4 + self.pair[1])[-1]

    @staticmethod
    def fromStr(char):
        i = int(char[0], 16)
        return Fields((i / 4, i % 4))

    @staticmethod
    def aa():
        return Fields((Fields.A, Fields.A))

    @staticmethod
    def ab():
        return Fields((Fields.A, Fields.B))

    @staticmethod
    def ba():
        return Fields((Fields.B, Fields.A))

    @staticmethod
    def bb():
        return Fields((Fields.B, Fields.B))


class Edge(object):
    '''Representation of an edge of a graph.'''
    def __init__(self, nodes, external_node=-1, fields=None, edge_id=None):
        '''Edge constructor.

        Args:
            nodes: pair of ints enumerating edge ends.
            external_node: which nodes are external. Default: -1.
            fields: Fields object with fields corresponding to the nodes.
        '''
        self.nodes = tuple(sorted(nodes))
        self.internal_nodes = tuple(
                [node for node in self.nodes if node != external_node])

        self.fields = None
        # Init fields annotating external edge.
        if fields:
            pair = list(fields.pair)
            for i in (0, 1):
                if nodes[i] == external_node:
                    pair[i] = Fields.EXTERNAL
            swap = (nodes[0] > nodes[1])
            if swap:
                pair = list(reversed(pair))

            self.fields = Fields(pair)

        self.edge_id = edge_id

    def __cmp__(self, other):
        cmp_nodes = cmp(self.internal_nodes, other.internal_nodes)
        if cmp_nodes:
          return cmp_nodes
        cmp_fields = cmp(self.fields, other.fields)
        return cmp_fields

    def copy(self, node_map=None):
        '''Creates a copy of the object with possible change of nodes.

        Args:
            node_map: dictionary mapping old nodes to new ones. Identity map
                is assumed for the missed keys.
        Returns:
            New Edge object.
        '''
        node_map = node_map or {}

        mapped_nodes = [node_map.get(node, node) for node in self.nodes]

        mapped_external_node = None
        if len(self.internal_nodes) == 1:
            external_node = self.nodes[0]
            if external_node == self.internal_nodes[0]:
                external_node = self.nodes[1]
            mapped_external_node = node_map.get(external_node, external_node)

        return Edge(mapped_nodes,
                    external_node=mapped_external_node,
                    fields=self.fields,
                    edge_id=self.edge_id)


class GraphState(object):
    SEP = ':'
    def __init__(self, edges, node_maps=None):
        node_maps = (node_maps or
                nickel.Canonicalize([edge.nodes for edge in edges]).node_maps)
        self.sortings = []
        for node_map in node_maps:
            mapped_edges = [edge.copy(node_map=node_map) for edge in edges]
            mapped_edges.sort()
            self.sortings.append(mapped_edges)
        min_edges = min(self.sortings)
        self.sortings = [edges for edges in self.sortings if edges == min_edges]
