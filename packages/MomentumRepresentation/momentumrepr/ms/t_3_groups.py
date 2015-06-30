#!/usr/bin/python
# -*- coding: utf8


__author__ = 'dima'


from momentumrepr import sym_coef
import graph_util_ms

group1 = list()
group1.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||::::")
group1.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_aA||::::")
group1.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa||::::")
group1.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|0a_Aa||::::")
group1.append("e12|33|45|6|e6|e6||:0a_aA_Aa|aA_aA|Aa_aA|aA|0A_aA|0a_Aa||::::")
group1.append("e12|33|45|6|e6|e6||:0a_Aa_aA|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||::::")
group1.append("e12|33|45|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||::::")
group1.append("e12|33|45|6|e6|e6||:0a_Aa_Aa|Aa_Aa|Aa_aA|Aa|0A_aA|0a_Aa||::::")

group2 = list()
group2.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|0a|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|Aa|0a_aA|Aa_Aa||::::")
group2.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_Aa|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|::::")
group2.append("e12|23|4|e5|e6|66||:0a_Aa_aA|aA_Aa|aA|0A_aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|aA_aA|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0a_Aa_aA|0A_aA|Aa_aA|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|Aa_aA|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_aA|aA_aA|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||::::")
group2.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||::::")
group2.append("e12|e3|34|5|e6|66||:0a_aA_Aa|0a_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||::::")
group2.append("e12|e3|34|5|e6|66||:0A_aA_aA|0a_Aa|aA_aA|aA|0a_Aa|aA_aA||::::")
group2.append("e12|e3|34|5|e6|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||::::")
group2.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|::::")
group2.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|aA|0a|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|::::")
group2.append("e12|e3|44|56|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|::::")
group2.append("e12|e3|44|56|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::")
group2.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|0A|Aa_Aa||::::")
group2.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_aA|aA_Aa|0a|aA_aA||::::")
group2.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_Aa|aA_aA|aA_Aa|0a|aA_aA||::::")
group2.append("e12|e3|45|46|e|66||:0A_aA_aA|0a_aA|aA_Aa|aA_aA|0a|Aa_Aa||::::")
group2.append("e12|e3|45|46|e|66||:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|0A|aA_aA||::::")
group2.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|0a_Aa|aA_aA||::::")
group2.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_aA|Aa|0a_Aa|0A_aA|Aa_Aa||::::")
group2.append("e12|23|4|e5|e6|66||:0a_Aa_Aa|Aa_Aa|Aa|0a_Aa|0A_aA|Aa_Aa||::::")
group2.append("e12|23|4|e5|e6|66||:0A_aA_aA|Aa_aA|aA|0a_aA|0a_Aa|aA_aA||::::")
group2.append("e12|23|4|e5|e6|66||:0A_aA_aA|Aa_aA|aA|0a_Aa|0a_aA|Aa_Aa||::::")

group3 = list()
group3.append("e12|e3|e4|45|6|66||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||::::")
group3.append("e12|e3|e4|45|6|66||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa|aA_aA||::::")
group3.append("e12|e3|e4|45|6|66||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA|Aa_Aa||::::")
group3.append("e12|e3|e4|55|66|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||::::")
group3.append("e12|e3|e4|55|66|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||::::")
group3.append("e12|e3|e4|55|66|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|aA||::::")
group3.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|Aa|0a|::::")
group3.append("e12|e3|44|55|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::")
group3.append("e12|e3|44|55|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::")

group4 = list()
group4.append("e12|e3|e4|56|56|6||:0A_aA_aA|0a_Aa|0a_aA|Aa_Aa|aA_aA|Aa||::::")
group4.append("e12|e3|e4|56|56|6||:0a_Aa_Aa|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||::::")
group4.append("e12|e3|e4|56|56|6||:0a_Aa_aA|0A_aA|0a_Aa|aA_aA|Aa_Aa|Aa||::::")

graphs = list()
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_aA|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|::::")
graphs.append("e12|e3|45|45|6|6|e|:0a_Aa_Aa|0a_Aa|Aa_aA|Aa_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|::::")
graphs.append("e12|e3|45|45|6|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|Aa_aA|0a_aA|0a_Aa|aA||::::")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_aA|Aa||::::")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|aA_aA|aA_aA|0a_Aa|0a_Aa|Aa||::::")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|Aa||::::")
graphs.append("e12|34|56|e5|e6|6||:0A_aA_aA|Aa_aA|aA_aA|0a_Aa|0a_Aa|aA||::::")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|aA_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|aA_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|Aa|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_aA|Aa_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|aA_aA|aA|0a_aA|Aa_aA|aA|0a|::::")
graphs.append("e12|23|4|e5|56|6|e|:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|Aa|0a|::::")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|0a_aA||::::")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|0a_Aa||::::")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_aA||::::")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_Aa||::::")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|0a_Aa||::::")
graphs.append("e12|34|35|6|e6|e6||:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|0a_aA||::::")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|Aa_aA|0a|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_Aa|Aa_aA|0A|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA_aA|0a|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA_aA|0a|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_aA|aA_Aa|aA|Aa_aA|Aa_aA|0A|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_Aa|0A|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_aA|Aa|Aa_aA|Aa_aA|0A|0a|::::")
graphs.append("e12|23|4|56|56|e|e|:0a_Aa_Aa|Aa_Aa|Aa|Aa_aA|Aa_aA|0A|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|aA|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|aA_aA|aA|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|Aa_aA|aA|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|aA_Aa|Aa|0A|::::")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|aA_Aa|Aa|0A|::::")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa|Aa_Aa|Aa|0A|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|aA_aA|aA|Aa_aA|aA|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|aA_aA|aA|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa|Aa_Aa|Aa|0A|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|aA|Aa_aA|aA|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|Aa|0a|::::")
graphs.append("e12|e3|34|5|56|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA|aA_aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|aA_Aa|Aa_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|Aa|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0a_Aa|Aa_Aa|aA_Aa|aA|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|aA_aA|Aa_aA|Aa|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|Aa|Aa|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|aA_aA|Aa_aA|Aa|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_aA|0A_aA|Aa_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_aA_Aa|0a_Aa|Aa_Aa|Aa_Aa|Aa|Aa|0A|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_Aa|aA_aA|Aa_aA|Aa|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0a_Aa_Aa|0A_aA|Aa_Aa|aA_aA|aA|aA|0a|::::")
graphs.append("e12|e3|45|46|5|6|e|:0A_aA_aA|0a_aA|Aa_aA|aA_aA|aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|Aa|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|Aa|0a_Aa|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|Aa|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|Aa|0A_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|Aa|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|Aa|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|Aa_Aa|Aa|0A_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|Aa|0A_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_Aa|aA_aA|aA|0a_Aa|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|aA_Aa|Aa_Aa|aA|0A_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_Aa|aA|0a_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|aA_aA|aA|0a_Aa|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0a_Aa_Aa|Aa_Aa|aA_Aa|aA|0A_aA|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|Aa_aA|aA_aA|aA|0a_Aa|aA|0a|::::")
graphs.append("e12|34|35|6|e5|6|e|:0A_aA_aA|aA_aA|Aa_aA|aA|0a_Aa|aA|0a|::::")


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


def get_group4():
    result = list()
    for g in group4:
        g = graph_util_ms.from_str(g)
        result.append((g, sym_coef.sc(g)))
    return result


def get_all():
    return graphs + [get_group1(), get_group2(), get_group3(), get_group4()]


def get_all_sources():
    return graphs, ["get_group1", "get_group2", "get_group3", "get_group4"]