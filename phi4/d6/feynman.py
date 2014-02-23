#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys

import graphine
from reduction import reductor, sector, THREE_LOOP_REDUCTOR
from rggraphenv import symbolic_functions

import conserv
import comb
import d6
from graph_state_builder_static import gs_builder
from two_and_three_loop_d6 import THREE_LOOP_REDUCTOR_D6


e = symbolic_functions.e

def xindex():
    index = 0
    while True:
        yield index
        index += 1


def gen_static_d(graph):
    index = xindex()
    edges_map = dict([(index.next(), x) for x in graph.allEdges(nickel_ordering=True)])
    internal_edges = dict(map(lambda x: (x[0], x[1].nodes), filter(lambda x: 1 if not x[1].is_external() else None, edges_map.items())))
    print internal_edges
    conservations = conserv.Conservations(internal_edges)
    print conservations
    res = list()
    for i in comb.xUniqueCombinations(internal_edges.keys(), graph.getLoopsCount()):
        valid = True
        i_set = set(i)
        for c in conservations:
            if c & i_set == c:
                valid = False

                break
        if valid:
            res.append(i)
    return res


def find_master_sector_from_graph(g, some_reductor):
    found = False
    for graph_sector in reductor._enumerate_graph(g, some_reductor._propagators):
        if graph_sector in some_reductor._masters_graph:
            found = True
            break
    if found:
        return graph_sector
    else:
        return None


def edges_map_from_sector(graph_sector, some_reductor):
    gs_ = some_reductor._masters_graph[graph_sector]
    index = xindex()
    g_ = graphine.Graph.fromStr(gs_)
    edges_map = dict()
    for edge in g_.allEdges(nickel_ordering=True):
        edges_map[index.next()] = edge.colors[0]
    return edges_map


def d6_reduction(graph_sector, det, d6_reductor):
    res = 0
    for term in det:
        sector_index = [0]*9
        for var in term:
            sector_index[edges_map[var]] = 1
        term_sector = sector.Sector(*sector_index)*graph_sector
        res += term_sector

    ans = THREE_LOOP_REDUCTOR_D6.evaluate_sector(res)
    return ans





g = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))

det = gen_static_d(g)
print det

THREE_LOOP_REDUCTOR_D6.initIfNeed()
THREE_LOOP_REDUCTOR.initIfNeed()

graph_sector = find_master_sector_from_graph(g, THREE_LOOP_REDUCTOR_D6)
print "graph_sector", graph_sector

edges_map = edges_map_from_sector(graph_sector, THREE_LOOP_REDUCTOR_D6)
print "edges_map", edges_map

ans = d6_reduction(graph_sector, det, THREE_LOOP_REDUCTOR_D6)
print
print "ans", ans
print
print symbolic_functions.series(ans.evaluate(substitute_sectors=True, _d=6-2*e),e,0,7).expand()
print

ans_ = ans.evaluate(substitute_sectors=True, _d=6-2*e)

lambdas = list(graph_sector.propagators_weights)
for i in range(3):
    lambdas[i] += 1
print
print symbolic_functions.series(THREE_LOOP_REDUCTOR._masters[graph_sector],e,0,7).expand()

print
print
print symbolic_functions.series(d6.C6(lambdas, 3)/d6.C4(graph_sector.propagators_weights,3),e,0,7).expand()
print



z = (d6.C6(lambdas, 3)/d6.C4(graph_sector.propagators_weights,3)*THREE_LOOP_REDUCTOR._masters[graph_sector]-ans_)

res = -z.coeff(symbolic_functions.UNKNOWN, 0)/z.coeff(symbolic_functions.UNKNOWN, 1)

print
print
print
print symbolic_functions.series(res,e,0,6).expand()