#!/usr/bin/python
# -*- coding: utf8
import conserv
import comb

__author__ = 'mkompan'


import graphine

from graph_state_builder_static import gs_builder

import sys

g = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))


def xindex():
    index = 0
    while True:
        yield index
        index += 1

def gen_static_d(graph):
    index = xindex()
    edges_map = dict([(index.next(), x) for  x in graph.allEdges(nickel_ordering=True)])
    edges_map_ = dict([(i, edges_map[i].nodes) for i in edges_map])

    print edges_map.values()
    print [x.is_external() for x in edges_map.values()]
    print conserv.Conservations(edges_map_)
    for i in comb.xUniqueCombinations(edges_map_):
        pass

gen_static_d(g)


