#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graph_state_property
import graph_state
from rggraphutil import VariableAwareNumber


class Arrow(object):
    LEFT_ARROW = "<"
    RIGHT_ARROW = ">"
    NULL = "0"

    _VALUES = set((LEFT_ARROW, RIGHT_ARROW, NULL))

    class Externalizer(graph_state_property.PropertyExternalizer):
        def deserialize(self, string):
            return Arrow(string)

    def __init__(self, value):
        assert value in Arrow._VALUES, value
        self._value = value

    @property
    def value(self):
        return self._value

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def make_external(self, nodes, external_node):
        return Arrow(Arrow.NULL)

    def is_null(self):
        return self.value == Arrow.NULL

    def is_left(self):
        return self.value == Arrow.LEFT_ARROW

    def as_numeric(self):
        if self.is_null():
            return 0
        return 1 if self.is_left() else -1

    def __cmp__(self, other):
        return cmp(self.value, other.value)

    def __neg__(self):
        if self.is_null():
            return self
        return Arrow(Arrow.RIGHT_ARROW) if self.is_left() else Arrow(Arrow.LEFT_ARROW)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)


class StringExternalizer(graph_state_property.PropertyExternalizer):
    def deserialize(self, string):
        return None if string == str(None) else string


class VariableAwareNumberExternalizer(graph_state_property.PropertyExternalizer):
    def __init__(self, var_name):
        self._var_name = var_name

    def deserialize(self, string):
        pair = eval(string)
        assert len(pair) == 2
        return VariableAwareNumber(self._var_name, pair[0], pair[1])

    def serialize(self, obj):
        return str((obj.a, obj.b))


WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG = \
    graph_state.PropertiesConfig.create(graph_state_property.PropertyKey(name="weight",
                                                                         is_directed=False,
                                                                         externalizer=VariableAwareNumberExternalizer("l")),
                                        graph_state_property.PropertyKey(name="arrow",
                                                                         is_directed=True,
                                                                         externalizer=Arrow.Externalizer()),
                                        graph_state_property.PropertyKey(name="marker",
                                                                         is_directed=False,
                                                                         externalizer=StringExternalizer()))