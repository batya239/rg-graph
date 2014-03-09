#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'



# noinspection PyMethodMayBeStatic
class PropertyExternalizer(object):
    def serialize(self, obj):
        return str(obj)

    def deserialize(self, string):
        return eval(string)


class FakePropertyExternalizer(PropertyExternalizer):
    def deserialize(self, string):
        raise NotImplementedError()

    def serialize(self, obj):
        raise NotImplementedError()


class PropertyKey(object):
    def __init__(self,
                 name,
                 is_directed=False,
                 is_edge_property=True,
                 externalizer=FakePropertyExternalizer()):
        self._name = name
        self._is_directed = is_directed
        self._externalizer = externalizer
        self._is_edge_property = is_edge_property

    @property
    def is_edge_property(self):
        return self._is_edge_property

    @property
    def name(self):
        return self._name

    @property
    def is_directed(self):
        return self._is_directed

    @property
    def externalizer(self):
        return self._externalizer

    def __eq__(self, other):
        assert isinstance(other, PropertyKey)
        return self.name == other.name and \
               self.is_directed == other.is_directed and \
               self.externalizer == other.externalizer and \
               self.is_edge_property == other.is_edge_property

    def __hash__(self):
        h = hash(self.name)
        h = 31 * h + hash(self.is_directed)
        h = 31 * h + hash(self.externalizer)
        h = 31 * h + hash(self.is_edge_property)
        return h