#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from momentumrepr import sym_coef
import graph_util_ms

graphs = list()
graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|::::")
graphs.append("e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|::::")

graphs.append("e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|::::")

graphs.append("e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a|::::")
graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a|::::")
graphs.append("e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|::::")
graphs = map(lambda g: graph_util_ms.from_str(g), graphs)

group1 = list()
group1.append("e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|::::")
group1.append("e12|e3|34|5|55||:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA||::::")
group1.append("e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA||::::")

group2 = list()
group2.append("e12|e3|45|45|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa||::::")

group3 = list()
group3.append("e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA||::::")
group3.append("e12|23|4|e5|55||:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA||::::")
group3.append("e12|23|4|e5|55||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||::::")
group3.append("e12|23|4|e5|55||:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||::::")
group3.append("e12|34|35|e|55||:0A_aA_aA|aA_Aa|aA_aA|0a|Aa_Aa||::::")


def get_group1():
    result = list()
    for g in group1:
        g = graph_util_ms.from_str(g)
        result.append((g, sym_coef.sc(g)))
    return result


def get_group2():
    result = list()
    for g in group2:
        g = graph_util_ms.from_str(g)
        result.append((g, sym_coef.sc(g)))
    return result


def get_group3():
    result = list()
    for g in group3:
        g = graph_util_ms.from_str(g)
        result.append((g, sym_coef.sc(g)))
    return result


def get_all():
    return graphs + [get_group1(), get_group2(), get_group3()]


def get_all_sources():
    return graphs, ["get_group1", "get_group2", "get_group3"]