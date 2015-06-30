#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

base = 1 * 2
import collections
import swiginac
import math
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict

def symmetry_lines(graph_l):
    adjacencies = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    for e in graph_l.edges():
        adjacencies[frozenset(e.nodes)][e.fields] += 1
    count = 1
    for d in adjacencies.values():
        for i in d.values():
            count *= math.factorial(i)
    return count


def sc(graph_fs):
    v = len(graph_fs.to_graph_state().sortings)
    l = symmetry_lines(graph_fs)
    return swiginac.numeric(base if graph_fs.external_edges_count == 3 else 1)/swiginac.numeric(v*l)


def symmetry_coefficient(gs):
    external_edge_fields = dict()
    edges_count = dict()
    bubbles = dict()
    for edge in gs.edges:
        n1, n2 = edge.nodes
        if n1 == n2:
            bubbles[edge] += 1
        edges_count[edge] += 1

        if edge.is_external():
            if edge.fields is None:
                field = None
            else:
                field_ = list(edge.fields.pair)
                field_.remove('0')
                field = field_[0]
            external_edge_fields[field] += 1

    c = swiginac.numeric('1')

    for n in external_edge_fields.values():
        c *= swiginac.factorial(symbolic_functions.cln(n))

    for n in edges_count.values():
        c /= swiginac.factorial(symbolic_functions.cln(n))
    trace = reduce(lambda x, y: x + y, [0] + bubbles.values())
    c /= symbolic_functions.cln(2) ** trace

    return c / symbolic_functions.cln(len(gs.sortings))


import graph_util_mr
graphs = list()

# graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|")
# graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|")
# graphs.append("e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|23|4|e5|55||:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA||")
# graphs.append("e12|23|4|e5|55||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|23|4|e5|55||:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
# graphs.append("e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a|")
# graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|")
# graphs.append("e12|34|35|e|55||:0A_aA_aA|aA_Aa|aA_aA|0a|Aa_Aa||")
# graphs.append("e12|e3|34|5|55||:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA||")
# graphs.append("e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
# graphs.append("e12|e3|45|45|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")

graphs.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|aA_Aa|0a|aA_aA||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|0a|aA_aA||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_aA|aA_Aa|0a|aA_aA||")
graphs.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_Aa|aA_aA|0a|Aa_Aa||")
graphs.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|0A|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|aA_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|aA_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|Aa_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|Aa|0a_aA|Aa_Aa||")
graphs.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_Aa|aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|Aa|Aa|0A|")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|Aa_aA|0a_aA|0a_Aa|aA||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_aA|Aa||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_Aa|Aa||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|aA||")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|Aa||")
graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_aA||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0a_aA_Aa|aA_aA|Aa_aA|aA|0A_aA|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||")
graphs.append("e12|33|45|6|e6|e6||:0a_Aa_aA|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|Aa|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|Aa|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|Aa_aA|aA|0a|")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa|aA|0a|")
graphs.append("e12|e3|e4|45|6|66||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||")
graphs.append("e12|e3|e4|45|6|66||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||")
graphs.append("e12|e3|e4|45|6|66||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA|Aa_Aa||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|0a_Aa||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_aA||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|0a_aA||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|Aa_aA|0a|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_Aa|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA_aA|0a|0a|")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA_aA|0a|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_aA|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_aA|aA_Aa|aA|Aa_aA|Aa_aA|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_aA|Aa|Aa_aA|Aa_aA|0A|0a|")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_Aa|Aa_aA|0A|0a|")
graphs.append("e12|e3|e4|55|66|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||")
graphs.append("e12|e3|e4|55|66|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
graphs.append("e12|e3|e4|55|66|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|56|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|aA_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|Aa_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|aA_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|Aa_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|Aa_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|aA_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|aA_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|Aa_aA|aA|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|Aa_Aa|Aa|0A|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|Aa|0a|")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|aA_aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|Aa|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|Aa|aA|0a|")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0a_Aa|0A_aA|Aa_Aa||")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa|aA_aA||")
graphs.append("e12|23|4|e5|e6|66||:0A_aA_aA|Aa_aA|aA|0a_aA|0a_Aa|aA_aA||")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_aA|Aa|0a_Aa|0A_aA|Aa_Aa||")
graphs.append("e12|23|4|e5|e6|66||:0A_aA_aA|Aa_aA|aA|0a_Aa|0a_aA|Aa_Aa||")
graphs.append("e12|23|4|e5|e6|66||:0a_Aa_aA|aA_Aa|aA|0A_aA|0a_Aa|aA_aA||")
graphs.append("e12|e3|e4|56|56|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||")
graphs.append("e12|e3|e4|56|56|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")
graphs.append("e12|e3|e4|56|56|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|Aa|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|Aa|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_Aa|aA_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|Aa|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_Aa|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|aA|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|Aa|0A_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|Aa|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|aA|0a|")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|Aa|0a|")
graphs.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|")
graphs.append("e12|e3|44|55|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|")
graphs.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|")
graphs = map(lambda g: graph_util_mr.from_str_alpha(g + ":::::"), graphs)

#
# import graphine
# import uv
# import configure_mr
# configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.CLN_TWO * symbolic_functions.e).with_target_loops_count(3).\
#         with_maximum_points_number(5000000).\
#         with_absolute_error(10e-10).\
#         with_relative_error(10e-8).\
#         with_integration_algorithm("suave").\
#         with_debug(True).configure()
# # if "e12|e3|45|46|e|66||" not in str(a_graph):
# #     return a_graph
#
# # no_tadpoles = graphine.filters.no_tadpoles
# # one_irreducible = graphine.filters.one_irreducible
# # target_sg = None
# #
# # for g in graphs:
# #     has2 = False
# #     for sg in g.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition):
# #         if uv.uv_index(sg) == 2:
# #             has2 = True
# #             if sg.loops_count == 1:
# #                 has2 = False
# #                 break
# #     if has2:
# #         print "graphs.append((graph_util_ms.from_str(\"" + str(g) + "\"), " + symbolic_functions.to_internal_code(str(sc(g)), strong=True) + "))"
# # exit(239)
#
#
# #
# # for g in graphs:
# #     str_g = str(g)
# #     if str_g.startswith("e12|e3|44|56|5|6|e|"):
# #         continue
# #     if str_g.startswith("e12|e3|34|5|e6|66||"):
# #         continue
# #     if str_g.startswith("e12|e3|45|46|e|66||"):
# #         continue
# #     if str_g.startswith("e12|23|4|e5|e6|66||"):
# #         continue
# #     # x = 0
# #     # x += 1 if "11" in str(g) else 0
# #     # x += 1 if "22" in str(g) else 0
# #     # x += 1 if "33" in str(g) else 0
# #     # x += 1 if "44" in str(g) else 0
# #     # x += 1 if "55" in str(g) else 0
# #     # x += 1 if "66" in str(g) else 0
# #     # if x == 2:
# #     print "graphs.append(graph_util_ms.from_str(\"" + str(g) + "\"), " + symbolic_functions.to_internal_code(str(sc(g)), strong=True) + "))"
#
#
# # g = graph_util_mr.from_str_alpha("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_aA||:::::")
# # g = graph_util_mr.from_str_alpha("e11|e|:0A_aA_aA|0a|:::::")
# #
# # print sc(g)
# # exit(2392)
#
#
# def remove_bubble(a_graph):
#     import graphine
#     import uv
#
#     # if "e12|e3|45|46|e|66||" not in str(a_graph):
#     #     return a_graph
#
#     no_tadpoles = graphine.filters.no_tadpoles
#     one_irreducible = graphine.filters.one_irreducible
#     target_sg = None
#     for sg in a_graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition):
#         if sg.loops_count != 1:
#             continue
#         if not str(sg).startswith("e11|e|"):
#             continue
#         target_sg = sg
#         break
#     if target_sg is None:
#         return a_graph
#     new_graph, new_v = a_graph.shrink_to_point(target_sg.edges(), with_aux_info=True)
#     v_edges = new_graph.edges(new_v)
#     assert len(v_edges) == 2
#     new_graph = new_graph.shrink_to_point([v_edges[0]])
#     # print new_graph
#     return graphine.Graph(new_graph.to_graph_state())
#
#
# def contains_two_bubbles(a_graph):
#     import graphine
#     import uv
#
#     no_tadpoles = graphine.filters.no_tadpoles
#     one_irreducible = graphine.filters.one_irreducible
#     target_sg = list()
#     for sg in a_graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv.uv_condition):
#         # if sg.loops_count != 1:
#         #     continue
#         if str(sg).startswith("e11|e|") or str(sg).startswith("e12|e3|33||"):
#             target_sg.append(sg)
#
#     return len(target_sg) == 2
#
# # target_g = contains_two_bubbles(g)
# # print target_g
# #
# # for g in graphs:
# #     if contains_two_bubbles(g) == target_g:
# #         print "graphs.append((graph_util_ms.from_str(\"" + str(g) + "\"), " + symbolic_functions.to_internal_code(str(sc(g)), strong=True) + "))"
# #
