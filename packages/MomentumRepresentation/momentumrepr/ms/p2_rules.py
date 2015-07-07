#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import graph_util_ms
import graphine
import graph_state
from rggraphenv import symbolic_functions

RULES = dict()


def find(graph):
    def remove_external_field(e):
        if not e.is_external():
            return e
        return e.copy(fields=graph_state.Fields("00"))

    return RULES[graphine.Graph(map(remove_external_field, graph)).__str__()]


def init_rule1():
    g_lhs = graph_util_ms.from_str("e12|e3|4|55|e5||:00_aA_aA|00_Aa|aA|Aa_Aa|00_aA||::::None|None|P2|None|None|None")

    c1 = -symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|4|55|e5||:00_aA_aA|00_Aa|aA|Aa_Aa|00_aA||::::")

    c2 = symbolic_functions.cln(1) / symbolic_functions.cln(2)
    g_rhs_2 = graph_util_ms.from_str("e12|e3|e4|44|:00_aA_aA|00_aA|00_Aa|aA_aA|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2}

    RULES[g_lhs.__str__()] = rule


def init_rule2():
    g_lhs = graph_util_ms.from_str("e12|e3|4|55|e5||:00_Aa_Aa|00_aA|Aa|aA_aA|00_Aa||::::None|None|P2|None|None|None")

    c1 = -symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|4|55|e5||:00_Aa_Aa|00_aA|Aa|aA_aA|00_Aa||::::")

    c2 = symbolic_functions.cln(1) / symbolic_functions.cln(2)
    g_rhs_2 = graph_util_ms.from_str("e12|e3|e4|44|:00_Aa_Aa|00_Aa|00_aA|Aa_Aa|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2}

    RULES[g_lhs.__str__()] = rule


def init_rule3():
    g_lhs = graph_util_ms.from_str("e12|e3|4|4|e|:00_aA_aA|00_Aa|aA|Aa|00|::::None|None|P2|P2|None")

    c1 = symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|4|4|e|:00_aA_aA|00_Aa|aA|Aa|00|::::")

    c2 = -symbolic_functions.cln(1)
    g_rhs_2 = graph_util_ms.from_str("e12|e3|3|e|:00_aA_aA|00_Aa|aA|00|::::")

    c3 = symbolic_functions.cln(1) / symbolic_functions.cln(4)
    g_rhs_3 = graph_util_ms.from_str("e12|e2|e|:00_aA_aA|00_aA|00|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2, g_rhs_3: c3}

    RULES[g_lhs.__str__()] = rule


def init_rule4():
    g_lhs = graph_util_ms.from_str("e12|e3|4|4|e|:00_aA_aA|00_Aa|aA|Aa|00|::::None|None|P2|None|None")

    c1 = -symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|4|4|e|:00_aA_aA|00_Aa|aA|Aa|00|::::")

    c2 = symbolic_functions.cln(1) / symbolic_functions.cln(2)
    g_rhs_2 = graph_util_ms.from_str("e12|e3|3|e|:00_aA_aA|00_Aa|aA|00|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2}

    RULES[g_lhs.__str__()] = rule


def init_rule5():
    g_lhs = graph_util_ms.from_str("e12|e3|4|4|e|:00_Aa_Aa|00_aA|Aa|aA|00|::::None|None|P2|None|None")

    c1 = -symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|4|4|e|:00_aA_aA|00_Aa|aA|Aa|00|::::")

    c2 = symbolic_functions.cln(1) / symbolic_functions.cln(2)
    g_rhs_2 = graph_util_ms.from_str("e12|e3|3|e|:00_aA_aA|00_Aa|aA|00|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2}

    RULES[g_lhs.__str__()] = rule


def init_rule6():
    g_lhs = graph_util_ms.from_str("e12|e3|3|e|:00_aA_aA|00_Aa|aA|00|::::None|None|P2|None|None")

    c1 = - symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|3|e|:00_aA_aA|00_Aa|aA|00|::::")

    c2 = symbolic_functions.cln(1) / symbolic_functions.cln(2)
    g_rhs_2 = graph_util_ms.from_str("e12|e2|e|:00_aA_aA|00_aA|00|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2}

    RULES[g_lhs.__str__()] = rule


def init_rule7():
    g_lhs = graph_util_ms.from_str("e12|e3|e3||:00_aA_aA|00_Aa|00_aA||::::None|None|None|P2")

    c1 = - symbolic_functions.cln(1)
    g_rhs_1 = graph_util_ms.from_str("e12|e3|3|e|:00_aA_aA|00_Aa|aA|00|::::")

    c2 = symbolic_functions.cln(1) / symbolic_functions.cln(2)
    g_rhs_2 = graph_util_ms.from_str("e12|e2|e|:00_aA_aA|00_aA|00|::::")

    rule = {g_rhs_1: c1, g_rhs_2: c2}

    RULES[g_lhs.__str__()] = rule

init_rule1()
init_rule2()
init_rule3()
init_rule4()
init_rule5()
init_rule6()
init_rule7()