#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import rg_graph_collections


class DisjointSet(object):
    def __init__(self, excluded_indices=set()):
        self._p = dict()
        self._excluded_indices = excluded_indices

    def _find(self, a):
        parent = self._p[a]
        return a if parent == a else self._find(parent)

    def add(self, a):
        if a in self._excluded_indices or a in self._p:
            return
        self._p[a] = a

    def union(self, a, b):
        if a in self._excluded_indices or b in self._excluded_indices:
            return
        if a not in self._p:
            self.add(a)
        if b not in self._p:
            self.add(b)
        p_a = self._find(a)
        p_b = self._find(b)
        self._p[p_b] = p_a

    def get_sets(self):
        root_to_elements = rg_graph_collections.emptySetDict()
        for e in self._p.keys():
            root_to_elements[self._find(e)].add(e)
        return root_to_elements.values()


