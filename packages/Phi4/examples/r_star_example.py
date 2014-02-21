#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from rggraphenv import storage, theory, symbolic_functions
import phi4

theory_name = "asd" #имя твоей теории, это маркер в сторадже, чтобы не загружать из других теорий значения
storage.initStorage(theory_name, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)
phi4.gfun_calculator.DEBUG = True

g = phi4.graph_util.graph_from_str("e11|e|", do_init_color=True)

r_star = phi4.r.KRStar(g,
                       phi4.MSKOperation(),
                       phi4.DEFAULT_SUBGRAPH_UV_FILTER,
                       description="this graphs was calculated on feb 6 2014",
                       use_graph_calculator=False)

print r_star

close_storage = storage.closeStorage(revert=True, doCommit=False, commitMessage=None)
