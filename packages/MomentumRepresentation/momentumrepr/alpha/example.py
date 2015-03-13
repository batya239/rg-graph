#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import time_versions
import graph_util_mr
import alpha_representation
import sector_decomposition

g = graph_util_mr.from_str_alpha("e12|23|3|e|:0A_aA_aA|aA_aA|aA|0a|::::")
g = alpha_representation.introduce_feynman_parameters(g)
d = alpha_representation.build_determinants_tilde_static(g).d
laws = alpha_representation.determine_conservation_laws(g)

for x in sector_decomposition.apply_sector_decomposition(g, laws, d, to_expr=True):
    print x
# for tv in time_versions.find_time_versions(g):
#     print "---"
#     for cs in tv.edges_cross_sections:
#         print cs