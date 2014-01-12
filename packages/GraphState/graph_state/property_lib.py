#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graph_state_property


class Arrow(object):
    LEFT_ARROW = 1
    RIGHT_ARROW = -LEFT_ARROW
    NULL = 0

    _VALUES = set((LEFT_ARROW, RIGHT_ARROW, NULL))

    class Externalizer(graph_state_property.PropertyExternalizer):
        def deserialize(self, string):
            return Arrow(int(string))

    def __init__(self, value):
        assert value in Arrow._VALUES
        self._value = value

    def __cmp__(self, other):
        return cmp(self.value, other.value)

    @property
    def value(self):
        return self._value

    def __hash__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)