#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import graph_util_ms
import graph_state
import graphine
from rggraphenv.symbolic_functions import cln, log, p

ln43 = log(cln(4)/cln(3))
ONE_LOOP = dict()
from rggraphenv import symbolic_functions
ONE_LOOP[graph_util_ms.from_str("e11|e|:00_aA_aA|00|::::").to_graph_state()] = {"iw": {-1: cln(1)/cln(4)}, "p2": {-1: -cln(1)/cln(8)}, "tau": {-1: -cln(1)/cln(2)}}
ONE_LOOP[graph_util_ms.from_str("e12|e2|e|:00_Aa_aA|00_aA|00|::::").to_graph_state()] = {"log": {-1: cln(1)/cln(4)}}
assert len(ONE_LOOP) == 2

TWO_LOOPS = dict()
# TWO_LOOPS[graph_util_ms.from_str("e12|e3|e4|44||:00_Aa_aA|00_aA|00_Aa|aA_aA||::::").to_graph_state()] = {"log": {-2: cln(1)/cln(64), -1: -cln(3)/cln(32)-ln43/cln(64)}}
# TWO_LOOPS[graph_util_ms.from_str("e12|e3|e4|44||:00_aA_aA|00_Aa|00_aA|Aa_Aa||::::").to_graph_state()] = {"log": {-2: cln(3)/cln(128), -1: -cln(3)*ln43/cln(128)-cln(1)/cln(32)}}
# TWO_LOOPS[graph_util_ms.from_str("e12|e3|e4|44||:00_Aa_Aa|00_Aa|00_aA|Aa_Aa||::::").to_graph_state()] = {"log": {-2: cln(3)/cln(128), -1: -cln(3)*ln43/cln(128)-cln(1)/cln(32)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|e4|44||:00_Aa_aA|00_aA|00_Aa|aA_aA||::::").to_graph_state()] = {"log": {-2: cln(1)/cln(64), -1: -cln(1)/cln(32)-ln43/cln(64)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|e4|44||:00_aA_aA|00_Aa|00_aA|Aa_Aa||::::").to_graph_state()] = {"log": {-2: cln(3)/cln(128), -1: -cln(3)*ln43/cln(128)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|e4|44||:00_Aa_Aa|00_Aa|00_aA|Aa_Aa||::::").to_graph_state()] = {"log": {-2: cln(3)/cln(128), -1: -cln(3)*ln43/cln(128)}}


TWO_LOOPS[graph_util_ms.from_str("e12|34|34|e|e|:00_aA_aA|aA_aA|aA_aA|00|00|::::").to_graph_state()] = {"log": {-1: ln43*cln(3)/cln(8)}}
TWO_LOOPS[graph_util_ms.from_str("e12|34|34|e|e|:00_Aa_Aa|Aa_Aa|Aa_Aa|00|00|::::").to_graph_state()] = {"log": {-1: ln43*cln(3)/cln(8)}}

TWO_LOOPS[graph_util_ms.from_str("e12|34|34|e|e|:00_aA_aA|aA_aA|Aa_aA|00|00|::::").to_graph_state()] = {"log": {-1: ln43/cln(8)}}

TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_aA_aA|00_aA|aA_aA|aA|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (cln(1)+ln43)/cln(32)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_Aa_Aa|00_Aa|Aa_Aa|Aa|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (cln(1)+ln43)/cln(32)}}

TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_aA_aA|00_aA|Aa_aA|aA|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (cln(1)-3*ln43)/cln(32)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_Aa_Aa|00_Aa|aA_Aa|Aa|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (cln(1)-3*ln43)/cln(32)}}

TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_aA_aA|00_Aa|aA_aA|Aa|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (ln43-cln(1))/cln(32)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_Aa_Aa|00_aA|Aa_Aa|aA|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (ln43-cln(1))/cln(32)}}

TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_aA_aA|00_Aa|aA_aA|aA|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (cln(1)-3*ln43)/cln(32)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|34|4|e|:00_Aa_Aa|00_aA|Aa_Aa|Aa|00|::::").to_graph_state()] = {"log": {-2: -cln(1)/cln(32), -1: (cln(1)-3*ln43)/cln(32)}}
# assert len(TWO_LOOPS) == 9





# TWO_LOOPS[graph_util_ms.from_str("e12|23|3|e|:00_aA_aA|aA_aA|aA|00|::::").to_graph_state()] = {"iw": {-2: -cln(1)/cln(16), -1: (cln(1)-ln43)/cln(16)},
#                                                                                                "p2": {-2: cln(1)/cln(32), -1: -cln(7)/cln(192)+ln43/cln(16)},
#                                                                                                "tau": {-1: cln(1)/cln(8), -2: cln(1)/cln(8)}}
TWO_LOOPS[graph_util_ms.from_str("e12|23|3|e|:00_aA_aA|aA_aA|aA|00|::::").to_graph_state()] = {"iw": {-2: -cln(1)/cln(16), -1: (cln(1)-ln43)/cln(16)},
                                                                                               "p2": {-2: cln(1)/cln(32), -1: -cln(7)/cln(192)+ln43/cln(16)},
                                                                                               "tau": {-1: -cln(1)/cln(8), -2: cln(1)/cln(8)}}

# TWO_LOOPS[graph_util_ms.from_str("e12|e3|33||:00_aA_aA|00_Aa|aA_aA||::::").to_graph_state()] = {"iw": {-2: cln(1)/cln(64), -1: -cln(3)/cln(32)-ln43/cln(64)},
#                                                                                               "p2": {-2: -cln(3)/cln(256), -1: cln(3)*ln43/cln(256)+cln(67)/cln(1536)},
#                                                                                               "tau": {-1: -cln(1)/cln(8)}}
TWO_LOOPS[graph_util_ms.from_str("e12|e3|33||:00_aA_aA|00_Aa|aA_aA||::::").to_graph_state()] = {"iw": {-2: cln(1)/cln(64), -1: -cln(1)/cln(32)-ln43/cln(64)},
                                                                                                "p2": {-2: -cln(3)/cln(256), -1: cln(3)*ln43/cln(256)+cln(19)/cln(1536)},
                                                                                                "tau": {-1: cln(3)/cln(32)}}
# # assert len(TWO_LOOPS) == 11
# a = TWO_LOOPS[graph_util_ms.from_str("e12|23|3|e|:00_aA_aA|aA_aA|aA|00|::::").to_graph_state()]["p2"][-1]
# b = TWO_LOOPS[graph_util_ms.from_str("e12|e3|33||:00_aA_aA|00_Aa|aA_aA||::::").to_graph_state()]["p2"][-1]/2
# print a+b
# exit(1)


def kr1(graph, operation):
    graph = graphine.Graph(map(lambda e: e.copy(fields=graph_state.Fields("00")) if e.is_external() else e, graph))
    if graph.loops_count == 1:
        return ONE_LOOP[graph.to_graph_state()][operation]
    elif graph.loops_count == 2:
        return TWO_LOOPS[graph.to_graph_state()][operation]
    assert False


def value(graph, operation):
    graph = graphine.Graph(map(lambda e: e.copy(fields=graph_state.Fields("00")) if e.is_external() else e, graph))
    if graph.loops_count == 1:
        return ONE_LOOP[graph.to_graph_state()][operation]
    assert False
