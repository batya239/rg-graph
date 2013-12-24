#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

from collections import namedtuple
import graph_state

# noinspection PyMethodMayBeStatic
class PropertyExternalizer(object):
    def serialize(self, obj):
        return str(obj)

    def deserialize(self, string):
        return eval(string)


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

PropertyKey = namedtuple('PropertyKey', ('name', 'is_directed', 'externalizer'))


class Properties(object):
    def __init__(self, properties_config=None, **kwargs):
        assert properties_config is not None
        self._properties_config = properties_config
        self._key = None
        for p_name in self._properties_config.property_order:
            if p_name in kwargs:
                setattr(self, p_name, kwargs[p_name])

    @staticmethod
    def from_kwargs(**kwargs):
        properties_config = kwargs.get('properties_config', None)
        if properties_config is None:
            return None
        p = Properties(properties_config)
        for p_name in properties_config.property_order:
            setattr(p, p_name, kwargs.get(p_name, None))
        return p

    def has_property(self, name):
        return self._properties_config.has_property(name)

    def make_external(self, nodes, external_node):
        external_prop = Properties(properties_config=self._properties_config)
        for p_name in self._properties_config.property_order:
            v = getattr(self, p_name, None)
            if graph_state.Edge.MAKE_PROPERTY_EXTERNAL_METHOD_NAME in v.__class__.__dict__:
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



