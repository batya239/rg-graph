#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys
import graphine
import conserv
import comb
import d6
from graph_state_builder_static import gs_builder
from reduction import reductor, sector, THREE_LOOP_REDUCTOR
from rggraphenv import symbolic_functions
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


G = symbolic_functions.G
# d=6-2e
l = 2 - symbolic_functions.e

THREE_LOOP_REDUCTOR_D6 = reductor.Reductor("loop3",
                               "loop3D6",
                               [graphine.Graph.fromStr("e12|34|35|4|5|e|"),
                                graphine.Graph.fromStr("e12|34|34|5|5|e|"),
                                graphine.Graph.fromStr("e12|23|4|45|5|e|")],
                               3,
                               {graphine.Graph.fromStr("e12|34|34|5|5|e|"):
                                    symbolic_functions.evaluate(
                                        "Order(e**-5)"),
                                graphine.Graph.fromStr("e11|22|33|e|"): G(1, 1) ** 3,
                                graphine.Graph.fromStr("e112|22|e|"): G(1, 1) * G(1, 1) * G(2 - 2 * l, 1),
                                graphine.Graph.fromStr("e11|222|e|"): G(1, 1) * G(1, 1) * G(1 - l, 1),
                                graphine.Graph.fromStr("e1111|e|"): G(1, 1) * G(1 - l, 1) * G(1 - 2 * l, 1),
                                graphine.Graph.fromStr("e12|223|3|e|"):
                                    symbolic_functions.evaluate("1/1296*e**(-3)+7/15552*e**(-2)+313817/62208*e**(-1)"
                                                                "+(15150437/414720+7/648*zeta(3))+(14441330803/74649600"
                                                                "+49/7776*zeta(3)+7/38880*Pi**4)*e+(4071059940119/4478976000"
                                                                "-3450385/31104*zeta(3)+7/24*zeta(5)+49/466560*Pi**4)*e**2"
                                                                "+(1081922417840587/268738560000-113/648*zeta(3)**2"
                                                                "-166621117/207360*zeta(3)+49/288*zeta(5)+13/17496*Pi**6"
                                                                "-690077/373248*Pi**4)*e**3+(278092698777237551/16124313600000"
                                                                "-791/7776*zeta(3)**2-158835899483/37324800*zeta(3)"
                                                                "-150985/128*zeta(5)+91/209952*Pi**6+245/54*zeta(7)"
                                                                "-166621117/12441600*Pi**4-113/19440*zeta(3)*Pi**4)*e**4"
                                                                "+Order(e**5)")})



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
print "ans", ans

other = 0
for i,j in  ans._final_sector_linear_combinations._sectors_to_coefficient.items():

    print i, j
    print i, j, ans._masters[i]
    if i == graph_sector:
        A = j
    else:
        other += ans._masters[i]*j

#fake lambdas, if propagator weights == (0,1) => (0,1,2) and Gamma(\lambda_i)==1, so only sum(lambdas) is important
lambdas = list(graph_sector.propagators_weights)
for i in range(3):
    lambdas[i] += 1
print THREE_LOOP_REDUCTOR._masters[graph_sector]
res = ((d6.C6(lambdas, 3)/d6.C4(graph_sector.propagators_weights,3)*THREE_LOOP_REDUCTOR._masters[graph_sector]-other)/A).evaluate()


print symbolic_functions.series(res.subs(symbolic_functions.var('d')==6-2*e),e,0,6).expand()