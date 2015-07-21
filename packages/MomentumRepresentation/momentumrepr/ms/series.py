#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


from rggraphutil import zeroDict


class Series(object):
    def __init__(self, map):
        self._map = map

    def __add_or_sub(self, other, is_add):
        assert isinstance(other, Series)
        result = dict(other._map)
        for i, c in self._map.iteritems():
            if i in result:
                result[i] += c
            else:
                result[i] = c
        return Series(result)

    def __sub__(self, other):
        return self.__add_or_sub(other, False)

    def __add__(self, other):
        return self.__add_or_sub(other, True)
