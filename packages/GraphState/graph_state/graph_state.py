#!/usr/bin/python
# -*- coding: utf8 -*-

import itertools
import nickel
import sys


def chain_from_iterables(iterables):
    for it in iterables:
        for element in it:
            yield element

if  'chain_from_iterables' not in itertools.__dict__:
    itertools.chain_from_iterables = chain_from_iterables

class Fields(object):
    EXTERNAL = '0'
    STR_LEN = 2

    def __init__(self, pair):
        assert len(str(pair[0])) == 1
        assert len(str(pair[1])) == 1
        self._pair = str(pair[0]), str(pair[1])

    @property
    def pair(self):
        return self._pair

    def __cmp__(self, other):
        return cmp(self.pair, other.pair)

    def __hash__(self):
        return hash(self.pair)

    def copy(self, swap=False):
        if swap:
            return Fields(tuple(reversed(self.pair)))
        return Fields(self.pair)

    def __str__(self):
        return self.pair[0] + self.pair[1]

    @staticmethod
    def fromStr(string):
        return Fields(string)

    @staticmethod
    def fieldsToStr(seq):
        return ''.join([str(fields) for fields in seq])

    @staticmethod
    def fieldsFromStr(string):
        return [Fields.fromStr(string[i : i + Fields.STR_LEN])
            for i in range(0, len(string), Fields.STR_LEN)]


class Rainbow(object):
    '''Class of sequences assigned to the edge.'''
    def __init__(self, colors):
        self._colors = tuple(colors)

    @property
    def colors(self):
        return self._colors

    def __getitem__(self, item):
        return self._colors[item]

    def __cmp__(self, other):
        return cmp(self.colors, other.colors)

    def __len__(self):
        return len(self.colors)

    def __hash__(self):
        return hash(self.colors)

    def __str__(self):
        return str(self.colors)

    def __repr__(self):
        return str(self)

    @staticmethod
    def fromStr(string):
        return Rainbow(eval(string))


class Edge(object):
    '''Representation of an edge of a graph.'''
    def __init__(self, nodes, external_node=-1, fields=None, colors=None,
            edge_id=None):
        '''Edge constructor.

        Args:
            nodes: pair of ints enumerating edge ends.
            external_node: which nodes are external. Default: -1.
            fields: Fields object with fields corresponding to the nodes.
            colors: Rainbow object.
        '''
        self._nodes = tuple(sorted(nodes))
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

        self.colors = colors

        self.edge_id = edge_id

    @property
    def nodes(self):
        return self._nodes

    def key(self):
        return (self.internal_nodes, self.fields, self.colors)

    def __repr__(self):
        return "(%s, fields=%s, colors=%s)"%self.key()

    def __cmp__(self, other):
        return cmp(self.key(), other.key())

    def __hash__(self):
        return hash(self.key())

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
                    colors=self.colors,
                    edge_id=self.edge_id)


class GraphState(object):
    SEP = ':'
    NICKEL_SEP = nickel.Nickel.SEP
    def __init__(self, edges, node_maps=None):
        # Fields must be in every edge or in no one.
        fields_count = len([edge.fields for edge in edges if edge.fields])
        assert fields_count == 0 or fields_count == len(edges)

        node_maps = (node_maps or
                nickel.Canonicalize([edge.nodes for edge in edges]).node_maps)
        self.sortings = []
        for node_map in node_maps:
            mapped_edges = [edge.copy(node_map=node_map) for edge in edges]
            mapped_edges.sort()
            self.sortings.append(tuple(mapped_edges))
        min_edges = min(self.sortings)
        self.sortings = [edges for edges in self.sortings if edges == min_edges]

    @property
    def edges(self):
        return self.sortings[0]

    def __cmp__(self, other):
        return cmp(self.sortings[0], other.sortings[0])

    def __hash__(self):
        return hash(self.sortings[0])

    def __str__(self):
        nickel_edges = [edge.nodes for edge in self.sortings[0]]
        edges_str = nickel.Nickel(edges=nickel_edges).string

        fields_str = ''
        if self.sortings[0][0].fields:
            fields_chars = [str(edge.fields) for edge in self.sortings[0]]
            fields_chars_iter = iter(fields_chars)
            # Add separators to fields string so that it would look similar to
            # edge string.
            fields_chars_with_sep = []
            for char in edges_str:
                if char == self.NICKEL_SEP:
                    fields_chars_with_sep.append(self.NICKEL_SEP)
                else:
                    fields_chars_with_sep.append(fields_chars_iter.next())
            fields_str = ''.join(fields_chars_with_sep)

        colors_str = ''
        if [1 for edge in self.sortings[0] if edge.colors]:
            colors_str = str([str(edge.colors) for edge in self.sortings[0]])

        return edges_str + self.SEP + fields_str + self.SEP + colors_str

    @staticmethod
    def fromStr(string):
        edges_str, fields_str, colors_str = string.split(GraphState.SEP, 2)

        nickel_edges = nickel.Nickel(string=edges_str).edges
        if not fields_str:
            fields = [None] * len(nickel_edges)
        else:
            fields_no_sep = filter(lambda c: c != GraphState.NICKEL_SEP, fields_str)
            fields = Fields.fieldsFromStr(fields_no_sep)

        if not colors_str:
            colors_list = [None] * len(nickel_edges)
        else:
            colors_list = itertools.imap(Rainbow.fromStr, eval(colors_str))

        edges = []
        for nodes, fields, colors in itertools.izip(nickel_edges, fields, colors_list):
            edges.append(Edge(nodes, fields=fields, colors=colors))
        assert len(edges) == len(nickel_edges)

        return GraphState(edges)

