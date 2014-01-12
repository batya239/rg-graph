#!/usr/bin/python
# -*- coding: utf8 -*-

import itertools
import nickel
import graph_state
import graph_state_property


def chain_from_iterables(iterables):
    for it in iterables:
        for element in it:
            yield element


if 'chain_from_iterables' not in itertools.__dict__:
    itertools.chain_from_iterables = chain_from_iterables


class Properties(object):
    def __init__(self, properties_config=None, **kwargs):
        assert properties_config is not None
        self._properties_config = properties_config
        self._key = None
        for p_name in self._properties_config.property_order:
            if p_name in kwargs:
                setattr(self, p_name, kwargs[p_name])

    @property
    def properties_config(self):
        return self._properties_config

    @staticmethod
    def from_kwargs(**kwargs):
        properties_config = kwargs.get('properties_config', None)
        if properties_config is None:
            return None
        p = Properties(properties_config)
        for p_name in properties_config.property_order:
            setattr(p, p_name, kwargs.get(p_name, None))
        return p

    def is_none(self):
        property_order = self._properties_config.property_order
        for p_name in property_order:
            v = getattr(self, p_name, None)
            if v is not None:
                return False
        return True

    def has_property(self, name):
        return self._properties_config.has_property(name)

    def make_external(self, nodes, external_node):
        external_prop = Properties(properties_config=self._properties_config)
        for p_name in self._properties_config.property_order:
            v = getattr(self, p_name, None)
            if Edge.MAKE_PROPERTY_EXTERNAL_METHOD_NAME in v.__class__.__dict__:
                v = v.make_external(nodes, external_node)
            setattr(external_prop, p_name, v)
        return external_prop

    def key(self):
        if self._key is None:
            raw_key = list()
            for p_name in self._properties_config.property_order:
                v = getattr(self, p_name, None)
                raw_key.append(v)
            self._key = tuple(raw_key)
        return self._key

    def update(self, **kwargs):
        p = Properties(self._properties_config)
        for p_name in self._properties_config.property_order:
            value = kwargs.get(p_name, None)
            if value is None:
                value = getattr(self, p_name, None)
            setattr(p, p_name, value)
        return p

    def __neg__(self):
        neg_prop = Properties(properties_config=self._properties_config)
        for p_name in self._properties_config.property_order:
            self_v = getattr(self, p_name, None)
            if self_v is None:
                neg_v = None
            else:
                directed = self._properties_config.is_directed(p_name)
                neg_v = -self_v if directed else self_v
            setattr(neg_prop, p_name, neg_v)
        return neg_prop

    # noinspection PyProtectedMember
    def __cmp__(self, other):
        if isinstance(other, Properties):
            assert self._properties_config is other._properties_config, "configs must be same to compare"
            property_order = self._properties_config.property_order
            for i in xrange(len(property_order)):
                p_name = property_order[i]
                self_v = getattr(self, p_name, None)
                other_v = getattr(other, p_name, None)
                if self_v is None:
                    if other_v is None:
                        continue
                    else:
                        return -1
                if other_v is None:
                    return 1
                cmp_res = cmp(self_v, other_v)
                if cmp_res:
                    return cmp_res
        raise AssertionError()

    def __repr__(self):
        property_order = self._properties_config.property_order
        builder = list()
        for i in xrange(len(property_order)):
            p_name = property_order[i]
            self_v = getattr(self, p_name, None)
            builder.append("%s=%s" % (p_name, self_v))
        return ", ".join(builder)

    __str__ = __repr__


class PropertiesConfig(object):
    def __init__(self, property_order, property_directionality, property_externalizer):
        self._property_order = property_order
        self._property_directionality = property_directionality
        self._property_externalizer = property_externalizer

    @property
    def property_order(self):
        return self._property_order

    def externalizer(self, p_name):
        return self._property_externalizer[p_name]

    def properties_count(self):
        return len(self._property_order)

    def is_directed(self, property_name):
        return self._property_directionality[property_name]

    def has_property(self, property_name):
        return property_name in self._property_directionality

    def new_edge(self, nodes, external_node=-1, edge_id=None, **kwargs):
        if len(kwargs):
            kwargs['properties_config'] = self
        return graph_state.Edge(nodes, external_node, edge_id, **kwargs)

    def graph_state_from_str(self, string):
        return graph_state.GraphState.fromStr(string, properties_config=self)

    def new_properties(self, **kwargs):
        return Properties(self, **kwargs)

    def __len__(self):
        return self._property_directionality

    @staticmethod
    def create(*property_keys):
        property_order = [None] * len(property_keys)
        property_directionality = dict()
        property_externalizer = dict()
        for i, k in enumerate(property_keys):
            property_order[i] = k.name
            property_directionality[k.name] = k.is_directed
            property_externalizer[k.name] = k.externalizer
        return PropertiesConfig(property_order, property_directionality, property_externalizer)


class Fields(object):
    EXTERNAL = '0'
    STR_LEN = 2

    class Externalizer(graph_state_property.PropertyExternalizer):
        def deserialize(self, string):
            return Fields.fromStr(string)

    def __init__(self, pair):
        assert len(str(pair[0])) == 1
        assert len(str(pair[1])) == 1
        self._pair = str(pair[0]), str(pair[1])

    def make_external(self, nodes, external_node):
        if external_node is nodes[0]:
            return Fields((Fields.EXTERNAL, self.pair[1]))
        else:
            return Fields((self.pair[0], Fields.EXTERNAL))

    @property
    def pair(self):
        return self._pair

    def __neg__(self):
        return Fields((self.pair[1], self.pair[0]))

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

    def __repr__(self):
        return str(self)

    @staticmethod
    def externalizer():
        return Fields.Externalizer()

    @staticmethod
    def fromStr(string):
        return Fields(string)

    @staticmethod
    def fieldsToStr(seq):
        return ''.join([str(fields) for fields in seq])

    @staticmethod
    def fieldsFromStr(string):
        return [Fields.fromStr(string[i: i + Fields.STR_LEN])
                for i in range(0, len(string), Fields.STR_LEN)]


class Rainbow(object):
    """
    Class of sequences assigned to the edge.
    Stores all input attributes as tuple ex:
        colors: [1,2] self._colors: (1,2)
        colors: 1     self._colors: (1,)
    """

    class Externalizer(graph_state_property.PropertyExternalizer):
        def deserialize(self, string):
            return Rainbow.fromObject(string)

    def __init__(self, colors):
        if isinstance(colors, Rainbow):
            self._colors = colors.colors
        else:
            self._colors = tuple(colors) if isinstance(colors, (list, set, tuple)) else (colors, )

    @property
    def colors(self):
        """
        main method to access data from colors
        """
        return self._colors

    def make_external(self, nodes, external_node):
        return self

    def __getitem__(self, item):
        return self._colors[item]

    def __cmp__(self, other):
        if isinstance(other, tuple):
            return cmp(self.colors, other)
        return cmp(self.colors, other.colors)

    def __len__(self):
        return len(self.colors)

    def __hash__(self):
        return hash(self.colors)

    def __str__(self):
        return str(self.colors)

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        if isinstance(other, Rainbow):
            return Rainbow(self.colors + other.colors)
        raise AssertionError()

    @staticmethod
    def externalizer():
        return Rainbow.Externalizer()

    @staticmethod
    def fromObject(obj):
        if obj is None:
            return None
        elif isinstance(obj, str):
            return Rainbow(eval(obj))
        else:
            return Rainbow(obj)


DEFAULT_PROPERTIES_CONFIG = PropertiesConfig.create(graph_state_property.PropertyKey(name="colors",
                                                                                     is_directed=False,
                                                                                     externalizer=Rainbow.externalizer()),
                                                    graph_state_property.PropertyKey(name="fields",
                                                                                     is_directed=True,
                                                                                     externalizer=Fields.externalizer()))


class Edge(object):
    """Representation of an edge of a graph."""

    #if this attribute is True than any new Edge will be generated with unique edge_id
    CREATE_EDGES_INDEX = True
    NEXT_EDGES_INDEX = 1
    MAKE_PROPERTY_EXTERNAL_METHOD_NAME = "make_external"

    def __init__(self, nodes, external_node=-1, edge_id=None, **kwargs):
        """Edge constructor.

        Args:
            nodes: pair of ints enumerating edge ends.
            external_node: which nodes are external. Default: -1.
            fields: Fields object with fields corresponding to the nodes.
            colors: Rainbow object.
        """
        self._nodes = tuple(sorted(nodes))
        self.internal_nodes = tuple([node for node in self.nodes if node != external_node])
        self.external_node = external_node
        properties = kwargs.get('properties', None)
        if properties is None:
            if 'properties_config' not in kwargs:
                kwargs['properties_config'] = DEFAULT_PROPERTIES_CONFIG
            properties = Properties.from_kwargs(**kwargs)
        swap = (nodes[0] > nodes[1])
        if properties is not None and self.is_external():
            properties = properties.make_external(nodes, external_node)
        self._properties = properties if not swap or properties is None else -properties

        if edge_id is not None:
            self.edge_id = edge_id
        else:
            if Edge.CREATE_EDGES_INDEX:
                self.edge_id = Edge.NEXT_EDGES_INDEX
                Edge.NEXT_EDGES_INDEX += 1
            else:
                self.edge_id = None

    def __getattr__(self, item):
        if self._properties is None:
            return None
        elif self._properties.has_property(item):
            return getattr(self._properties, item)
        return None

    def is_external(self):
        return len(self.internal_nodes) == 1

    @property
    def nodes(self):
        return self._nodes

    def key(self):
        if '_key' not in self.__dict__:
            # noinspection PyAttributeOutsideInit
            self._key = (self.internal_nodes,)
            if self._properties:
                self._key += self._properties.key()
        return self._key

    def __repr__(self):
        return "(%s, %s)" % (self.internal_nodes, str(self._properties))

    __str__ = __repr__

    def __cmp__(self, other):
        return cmp(self.key(), other.key())

    def __hash__(self):
        if '_hash' not in self.__dict__:
            #noinspection PyAttributeOutsideInit
            self._hash = hash(self.key())
        return self._hash

    def cut_tadpole(self):
        nodes_set = set(self.nodes)
        assert len(nodes_set) == 1 and not self.is_external()
        node = nodes_set.pop()
        nodes1 = (node, self.external_node)
        nodes2 = (self.external_node, node)
        return tuple(map(lambda n: Edge(n, external_node=self.external_node, properties=self._properties.make_external(n, self.external_node)), (nodes1, nodes2)))

    def copy(self, node_map=None, **kwargs):
        """
        Creates a copy of the object with possible change of nodes.

        Args:
            node_map: dictionary mapping old nodes to new ones. Identity map
                is assumed for the missed keys.
        Returns:
            New Edge object.
        """
        node_map = node_map or {}

        mapped_nodes = [node_map.get(node, node) for node in self.nodes]

        mapped_external_node = node_map.get(self.external_node, self.external_node)

        properties_is_none = self._properties.is_none()
        updated_properties = None if properties_is_none else self._properties.update(**kwargs)
        if updated_properties is None:
            updated_properties = kwargs.get('properties', None)
            if updated_properties is None:
                if 'properties_config' not in kwargs:
                    kwargs['properties_config'] = DEFAULT_PROPERTIES_CONFIG
                updated_properties = Properties.from_kwargs(**kwargs)

        if mapped_external_node in mapped_nodes:
            updated_properties = updated_properties.make_external(mapped_nodes, mapped_external_node)
        return Edge(mapped_nodes,
                    external_node=mapped_external_node,
                    properties=updated_properties)


# noinspection PyProtectedMember
class GraphState(object):
    SEP = ':'
    SEP2 = "_"
    NICKEL_SEP = nickel.Nickel.SEP

    def __init__(self, edges, node_maps=None, default_properties=None):
        # Fields must be in every edge or defaultFields must be not None.
        properties_count = len([edge._properties for edge in edges if edge._properties])
        assert properties_count == 0 or properties_count == len(edges) or default_properties is not None, \
            ("properties_count =  %s, len(edges) = %s, default_properties = %s" % (properties_count, len(edges), default_properties))

        node_maps = (node_maps or nickel.Canonicalize([edge.nodes for edge in edges]).node_maps)
        self.sortings = []
        for node_map in node_maps:
            mapped_edges = list()
            for edge in edges:
                props = default_properties if edge._properties.is_none() else edge._properties
                mapped_edges.append(edge.copy(node_map=node_map, properties=props))
            mapped_edges.sort()
            self.sortings.append(tuple(mapped_edges))
        min_edges = min(self.sortings)
        self.sortings = [edges for edges in self.sortings if edges == min_edges]
        self._properties_config = None if edges[0]._properties is None else edges[0]._properties._properties_config

    @property
    def edges(self):
        """
        returns ordered with nickel order edges which represents corresponding GraphState
        """
        return self.sortings[0]

    def __cmp__(self, other):
        return cmp(self.sortings[0], other.sortings[0])

    def __hash__(self):
        return hash(self.sortings[0])

    def __repr__(self):
        return str(self)

    def __str__(self):
        nickel_edges = [edge.nodes for edge in self.sortings[0]]
        edges_str = nickel.Nickel(edges=nickel_edges).string

        serialized = [edges_str]

        if self._properties_config is not None:
            for p_name in self._properties_config.property_order:
                externalizer = self._properties_config.externalizer(p_name)
                is_all_attrs_none = reduce(lambda b, edge: b and getattr(edge, p_name) is None, self.sortings[0], True)
                if is_all_attrs_none:
                    serialized.append('')
                    continue
                fields_chars = [externalizer.serialize((getattr(edge, p_name))) for edge in self.sortings[0]]
                fields_chars_iter = iter(fields_chars)
                # Add separators to fields string so that it would look similar to
                # edge string.
                fields_chars_with_sep = []
                for char in edges_str:
                    if char == self.NICKEL_SEP:
                        fields_chars_with_sep.append(self.NICKEL_SEP)
                    else:
                        if len(fields_chars_with_sep) and fields_chars_with_sep[-1] != self.NICKEL_SEP:
                            fields_chars_with_sep.append(self.SEP2)
                        fields_chars_with_sep.append(fields_chars_iter.next())
                serialized.append(''.join(fields_chars_with_sep))

        return self.SEP.join(serialized)

    @staticmethod
    def fromStr(string, properties_config=None):
        """
        creates GraphState object from nickel serialized string
        """
        if properties_config is None:
            properties_config = DEFAULT_PROPERTIES_CONFIG
        parts_count = 1 + properties_config.properties_count()
        splitted_string = string.split(GraphState.SEP, parts_count)
        splitted_len = len(splitted_string)
        empty_properties = splitted_len == 1
        assert empty_properties or splitted_len == parts_count

        nickel_edges = nickel.Nickel(string=splitted_string[0]).edges

        if not empty_properties:
            raw_properties = splitted_string[1:]
            un_transposed_properties = dict()
            for (r_property_line, p_name) in itertools.izip(raw_properties, properties_config.property_order):
                if r_property_line != '':
                    r_properties = reduce(lambda _list, line: _list + line.split(GraphState.SEP2), r_property_line.split(nickel.Nickel.SEP),
                                          list())[:-1]
                    r_properties = filter(lambda p: len(p), r_properties)
                    externalizer = properties_config.externalizer(p_name)
                    un_transposed_properties[p_name] = map(lambda raw_prop: externalizer.deserialize(raw_prop), r_properties)
                else:
                    un_transposed_properties[p_name] = [None] * len(nickel_edges)
            transposed_properties = list()
            for i in xrange(len(nickel_edges)):
                transposed_properties.append(dict({'properties_config': properties_config}))
            for (p_name, properties) in un_transposed_properties.iteritems():
                for p, m in itertools.izip(properties, transposed_properties):
                    m[p_name] = p
        else:
            transposed_properties = [None] * len(nickel_edges)

        edges = []
        for nodes, props in itertools.izip(nickel_edges, transposed_properties):
            edges.append(Edge(nodes, properties_config=properties_config) if props is None else Edge(nodes, **props))
        assert len(edges) == len(nickel_edges)

        return GraphState(edges)

    @staticmethod
    def fromStrOldStyle(string):
        parts = string.split(GraphState.SEP, 3)
        basement = parts[0].replace("-", GraphState.NICKEL_SEP)
        new_style_str = basement + GraphState.SEP
        assert len(parts) in (1, 3)
        if len(parts) == 1 or (not len(parts[1]) and not len(parts[2])):
            return GraphState.fromStr(basement, properties_config=DEFAULT_PROPERTIES_CONFIG)

        raw_old_fields = parts[1]
        raw_old_colors = parts[2]

        if len(raw_old_colors):
            colors_it = GraphState._raw_old_colors_tokenizer(raw_old_colors)
            for c in iter(parts[0]):
                if c == "-":
                    new_style_str += GraphState.NICKEL_SEP
                else:
                    add = "" if new_style_str[-1] == GraphState.SEP or new_style_str[-1] == GraphState.NICKEL_SEP else GraphState.SEP2
                    new_style_str += add + colors_it.next()

        new_style_str += GraphState.SEP
        if len(raw_old_fields):
            fields_it = GraphState._raw_old_fields_tokenizer(raw_old_fields)
            for c in iter(parts[0]):
                if c == "-":
                    new_style_str += GraphState.NICKEL_SEP
                else:
                    add = "" if new_style_str[-1] == GraphState.SEP or new_style_str[-1] == GraphState.NICKEL_SEP else GraphState.SEP2
                    new_style_str += add + fields_it.next()

        return GraphState.fromStr(new_style_str, properties_config=DEFAULT_PROPERTIES_CONFIG)


    @staticmethod
    def _raw_old_fields_tokenizer(raw_old_fields):
        f = ""
        for c in raw_old_fields:
            if len(f) == 2:
                yield f
                f = ""
            if c == "-":
                f = ""
            else:
                f += c

    @staticmethod
    def _raw_old_colors_tokenizer(raw_old_colors):
        for raw_color in eval(raw_old_colors):
            yield str(raw_color)