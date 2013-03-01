#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

class XSpaceRepresentation(object):
    def __init__(self, graph):
        assert len(graph.edges(graph.externalVertex)) == 2, "graph should has correct momentum flow"
        self._graph = graph

    @staticmethod
    def _doXSpaceRepresentation(graph):

