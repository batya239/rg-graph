#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import graph_util_ms
import configure_mr
import integration
import swiginac
from kr1 import compound_kr1, kr1_with_rules, kr1

from rggraphenv import symbolic_functions
configure_mr.Configure().with_dimension(symbolic_functions.cln(4) - symbolic_functions.CLN_TWO * symbolic_functions.e).with_target_loops_count(3).\
    with_maximum_points_number(20000000).\
    with_absolute_error(10e-10).\
    with_relative_error(10e-8).\
    with_integration_algorithm("suave").\
    with_debug(True).configure()

# graphs = list()
# graphs.append((graph_util_ms.from_str("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_aA||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|0a_Aa||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|33|45|6|e6|e6||:0a_aA_Aa|aA_aA|Aa_aA|aA|0A_aA|0a_Aa||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|33|45|6|e6|e6||:0a_Aa_aA|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||::::"), 1))

# graphs = list()
# graphs.append((graph_util_ms.from_str("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|0a|aA_aA||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|Aa|0a_aA|Aa_Aa||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_Aa|aA|0a_Aa|aA_aA||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|23|4|e5|e6|66||:0a_Aa_aA|aA_Aa|aA|0A_aA|0a_Aa|aA_aA||::::"), 1))

# graphs = list()
# graphs.append((graph_util_ms.from_str("e12|e3|e4|45|6|66||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|45|6|66||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|45|6|66||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA|Aa_Aa||::::"), 1))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|55|66|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||::::"), swiginac.numeric('1')/swiginac.numeric('2')))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|55|66|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||::::"), swiginac.numeric('1')/swiginac.numeric('2')))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|55|66|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||::::"), swiginac.numeric('1')/swiginac.numeric('2')))
# graphs.append((graph_util_ms.from_str("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|::::"), swiginac.numeric('1')/swiginac.numeric('2')))
# graphs.append((graph_util_ms.from_str("e12|e3|44|55|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::"), swiginac.numeric('1')/swiginac.numeric('2')))
# graphs.append((graph_util_ms.from_str("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::"), swiginac.numeric('1')/swiginac.numeric('2')))


# graphs = list()
# graphs.append((graph_util_ms.from_str("e12|e3|e4|56|56|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||::::"), 2))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|56|56|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||::::"), 2))
# graphs.append((graph_util_ms.from_str("e12|e3|e4|56|56|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||::::"), 2))

r = symbolic_functions.CLN_ZERO
from rggraphutil import zeroDict
r1 = zeroDict()

def multiply(dict_a, dict_b):
    dict_c = zeroDict()
    for k, v in dict_a.iteritems():
        for k2, v2 in dict_b.iteritems():
            dict_c[k + k2] += v * v2
    return dict_c

import t_2_groups
import t_3_groups
graphs = t_2_groups.get_all()
# graphs = t_3_groups.get_group3()
# f = open('log3l_2t_w','w')
with open('log3l_2t_tau','w') as f:
    # graphs = t_3_groups.get_all()
    for g in graphs:
        r = symbolic_functions.CLN_ZERO
        from rggraphutil import zeroDict
        r1 = zeroDict()
        op = compound_kr1 if isinstance(g, list) else kr1
        for t in op(g):
            p2_dotes = 0
            if len(t) == 3:
                p2_dotes = t[2]
            k = t[0]
            v = t[1]
            # r += integration.calculate_with_tau(k, "iw", p2_dotes) * v.eval_with_tau()
            dia_vl = integration.calculate(k, None, p2_dotes)
            r += integration.apply_tau(dia_vl, k) * v.eval_with_tau()
            diag_res = dia_vl
            multiplier_res = v.eval_with_error()
            for k, v in multiply(diag_res, multiplier_res).items():
                r1[k] += v
        #ith open('log20kk2','wa+') as f:
        f.write(str(g) + "\n")
        f.write(str(symbolic_functions.pole_part(r, remove_order=False).evalf()) + "\n")
        f.write(str(integration.K(r1)) + "\n")
        f.flush()
        print "RESULT", symbolic_functions.pole_part(r, remove_order=False).evalf()
        print "RESULT", integration.K(r1)


# f.close()
# # ggg = graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|aA_aA|aA|0a|::::")
# ggg = graph_util_ms.from_str("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|::::")
# r = symbolic_functions.CLN_ZERO
# for t in k1_with_rules(ggg):
#     k = t[0]
#     print "loops", k.loops_count
#     print k
#     v = t[1]
#     print v
#     print v.eval_with_tau()
#     diag_val = integration.calculate_with_tau(k, None)
#     print "diag_val", k, diag_val
#     r += diag_val * v.eval_with_tau()
#     print "---"
# print "RESULT", symbolic_functions.pole_part(r, remove_order=False)
# print "RESULT", symbolic_functions.pole_part(r, remove_order=False).coeff(symbolic_functions.e ** (-1)).simplify_indexed()
# print "RESULT", symbolic_functions.pole_part(r, remove_order=False).coeff(symbolic_functions.e ** (-2)).simplify_indexed()
#{-2: 0.011939545030540554+/-1.312745711111111e-07, -3: 0.0029296875+/-0, -1: 0.004361881644797129+/-7.004578744444444e-07}

# ggg = graph_util_ms.from_str("e12|e3|33||:00_aA_aA|00_Aa|aA_aA||::::")
# import t_2_groups
# ggg = t_2_groups.get_group3()
# import hardcoded
# r = symbolic_functions.CLN_ZERO
# for t in compound_kr1(ggg):
#     k = t[0]
#     p2_dotes = 0
#     if len(t) == 3:
#         p2_dotes = t[2]
#     print "loops", k.loops_count
#     print "dotes", p2_dotes
#     print "graph", k
#     v = t[1]
#     print v
#     print v.eval_with_tau()
#     diag_val = integration.calculate_with_tau(k, None, p2_dotes)
#     print "diag_val", k, diag_val
#     r += diag_val * v.eval_with_tau()
#     print "---"
# print "RESULT", symbolic_functions.pole_part(r, remove_order=False).evalf()
# print "RESULT", symbolic_functions.pole_part(r, remove_order=False).coeff(symbolic_functions.e ** (-1)).simplify_indexed().evalf()
# print "RESULT", symbolic_functions.pole_part(r, remove_order=False).coeff(symbolic_functions.e ** (-2)).simplify_indexed().evalf()
# # print "RESULT", symbolic_functions.pole_part(r, remove_order=False).coeff(symbolic_functions.e ** (-3)).simplify_indexed().evalf()
# # print "REAL -1", hardcoded.kr1(ggg, "tau").get(-1, symbolic_functions.CLN_ZERO).evalf()
# # print "REAL -2", hardcoded.kr1(ggg, "tau").get(-2, symbolic_functions.CLN_ZERO).evalf()
#{-2: 0.011939545030540554+/-1.312745711111111e-07, -3: 0.0029296875+/-0, -1: 0.004361881644797129+/-7.004578744444444e-07}


# graphs = list()
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|Aa_aA|0a_aA|0a_Aa|aA||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_aA|Aa||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_Aa|Aa||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|aA||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|Aa||::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|0a_Aa||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_aA||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|0a_aA||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_Aa||::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|Aa_aA|0a|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_Aa|0A|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA_aA|0a|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA_aA|0a|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_aA|0A|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0a_Aa_aA|aA_Aa|aA|Aa_aA|Aa_aA|0A|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_aA|Aa|Aa_aA|Aa_aA|0A|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_Aa|Aa_aA|0A|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|aA_Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|Aa_Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|aA_Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|Aa_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|Aa_Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|aA_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|Aa_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|Aa|0A_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_Aa|aA_aA|aA|0a_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_Aa|aA|0a_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|aA|0A_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|Aa|0A_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|Aa|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|aA|0a|::::"))
# graphs.append(graph_util_ms.from_str("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|Aa|0a|::::"))
#
# f = open("123333.txt", "a+")
# for g in graphs[47:]:
#     r = symbolic_functions.CLN_ZERO
#     for t in kr1(g):
#         k = t[0]
#         print "loops", k.loops_count
#         print k
#         v = t[1]
#         print v
#         print v.eval_with_tau()
#         diag_val = integration.calculate_with_tau(k, None)
#         print "diag_val", k, diag_val
#         r += diag_val * v.eval_with_tau()
#         print "---"
#     print "RESULT:", symbolic_functions.pole_part(r, remove_order=False).evalf()
#     f.write(str(g) + "\n")
#     f.write(str(symbolic_functions.pole_part(r, remove_order=False).evalf()) + "\n")
