#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import reduction


DEBUG = True


def scalar_product_extractor(topology, graph):
    extracted_numerated_edges = list()
    if DEBUG:
        print "CAL", graph
    for e1, e2 in zip(topology.allEdges(nickel_ordering=True), graph.allEdges(nickel_ordering=True)):
        numerator = e2.arrow if not e2.arrow.is_null() else None
        if numerator:
            extracted_numerated_edges.append((e1, numerator))
    if not len(extracted_numerated_edges):
        if DEBUG:
            print "no scalar products"
        raise StopIteration()
    if len(extracted_numerated_edges) == 1:
        numerated_edge = extracted_numerated_edges[0]
        sign = -1 if numerated_edge[1].is_left() else 1

        sp = reduction.ScalarProduct(numerated_edge[0].colors[1],
                                     (1, ) + (0, ) * (len(numerated_edge[0].colors[1]) - 1),
                                     sign=sign)
        if DEBUG:
            print "sp", sp
        yield sp
    else:
        assert len(extracted_numerated_edges) == 2, ("graph must has only 2 numerated edges, actual = %s, graph = %s" % (extracted_numerated_edges, graph))
        common_vertex = (set(extracted_numerated_edges[0][0].nodes) & set(extracted_numerated_edges[1][0].nodes)).pop()
        adjusted_numerators = map(lambda (e, n): n if e.nodes[0] == common_vertex else -n, extracted_numerated_edges)
        sign = -1 if adjusted_numerators[0] == adjusted_numerators[1] else 1

        sp = reduction.ScalarProduct(extracted_numerated_edges[0][0].colors[1],
                                          extracted_numerated_edges[1][0].colors[1], sign=sign)
        if DEBUG:
            print "sp", sp
        yield sp


GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR = reduction.ScalarProductTwoAndThreeLoopsGraphCalculator(scalar_product_extractor)