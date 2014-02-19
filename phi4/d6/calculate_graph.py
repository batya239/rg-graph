#!/usr/bin/python
# -*- coding: utf8
import graphine
import rggraphenv

__author__ = 'mkompan'


from rggraphenv import storage, theory, symbolic_functions
import phi4
from two_and_three_loop_d6 import reduction_calculator_3loop, reduction_calculator_2loop, reduction_calculator_23loop

theory_name = "phi3" #имя твоей теории, это маркер в сторадже, чтобы не загружать из других теорий значения
DEFAULT_SUBGRAPH_UV_FILTER = graphine.filters.isRelevant(phi4.ir_uv.UV_RELEVANCE_CONDITION_6_DIM)

# #noinspection PyPep8Naming
# def G_d6(alpha, beta, d=6-2*e):
#     if alpha == 1 and beta == 1:
#         return -1 / e /6
#     return _raw_g(alpha, beta, d=d) / _g11_d6(d=d)

# def _g11(d=6-2*e):
#     return _raw_g(1, 1, d=d) * (-6*e)


#FIXME: IRFILETR!!

storage.initStorage(theory_name, symbolic_functions.to_internal_code, graphStorageUseFunctions=True)


#когда я редукцию там пофиксю слегка, то всавлю код сюда же, который ее задействует


g = phi4.graph_util.graph_from_str("e12|e2|e|", do_init_color=True)
g = phi4.graph_util.graph_from_str("e11|e|", do_init_color=True)
#g = phi4.graph_util.graph_from_str("e12|23|3|e|", do_init_color=True)

phi4.r.DEBUG = True
rggraphenv.graph_calculator.addCalculator(reduction_calculator_2loop)

r_star = phi4.r.KRStar(g,
                       phi4.MSKOperation(),
                       DEFAULT_SUBGRAPH_UV_FILTER,
                       description="this graphs was calculated on feb 6 2014",
                       use_graph_calculator=True)
e = symbolic_functions.e
print "\n\nKR*(%s) = %s\n\n" % (g, r_star)
print symbolic_functions.safe_integer_numerators_strong(str(r_star))

close_storage = storage.closeStorage(revert=True, doCommit=False, commitMessage=None)



