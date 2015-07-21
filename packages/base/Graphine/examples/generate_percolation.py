#!/usr/bin/python
# -*- coding: utf8
#
# Generation of Feynman diagrams for percolation theory in statistical physics in order of 3-loops
# based on "static" diagrams of \phi^3 theory.
#
# run script:
# $ python generate_percolation.py
# expected output of script is:
#
# e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a| 1
# e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a| 1
# e12|34|35|e|55||:0A_aA_aA|aA_Aa|aA_aA|0a|Aa_Aa|| 1/2
# e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA|| 1/4
# e12|23|4|e5|55||:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA|| 1/2
# e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA|| 1/2
# e12|23|4|e5|55||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa|| 1/2
# e12|23|4|e5|55||:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa|| 1/2
# e12|e3|45|45|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa|| 1
# e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a| 1
# e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a| 1
# e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a| 1
# e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a| 1
# e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a| 1/4
# e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a| 1
# e12|e3|34|5|55||:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA|| 1/2
# e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a| 1/8
# e12|23|3|e|:0A_aA_aA|Aa_aA|aA|0a| 1
# e12|e3|33||:0A_aA_aA|0a_Aa|aA_aA|| 1/2
# e11|e|:0A_aA_aA|0a| 1/2

__author__ = 'batya239@gmail.com'

import diagram_generator
import sym_coef

three_loops = list()

three_loops.append("e12|23|4|45|5|e|")
three_loops.append("e12|34|35|e|55||")
three_loops.append("e12|e3|44|55|5||")
three_loops.append("e12|23|4|e5|55||")
three_loops.append("e12|e3|45|45|5||")
three_loops.append("e12|34|35|4|5|e|")
three_loops.append("e12|34|34|5|5|e|")
three_loops.append("e12|e3|34|5|55||")
three_loops.append("e12|33|44|5|5|e|")
three_loops.append("e12|23|3|e|")
three_loops.append("e12|e3|33|")
three_loops.append("e11|e|")

for gs in three_loops:
    for _g in diagram_generator.generate_fields(gs,
                                         possible_fields=["aA"],
                                         possible_external_fields="Aa",
                                         possible_vertices=["aaA", "aAA"],
                                         ignore_cycles=False,
                                         unlabeled_legs=True):
        print _g, sym_coef.symmetry_coefficient(_g)

# two_loops = list()
# two_loops.append("e12|e3|e4|44||")
# two_loops.append("e12|23|4|e4|e|")
# two_loops.append("e12|34|34|e|e|")
#
# for gs in two_loops:
#     for _g in diagram_generator.generate(gs,
#                                          possible_fields=["aA"],
#                                          possible_external_fields="Aaa",
#                                          possible_vertices=["aaA", "aAA"],
#                                          ignore_cycles=False,
#                                          unlabeled_legs=True):
#         print _g, sym_coef.symmetry_coefficient(_g)