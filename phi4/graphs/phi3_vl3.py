#!/usr/bin/python
# -*- coding: utf8

import conserv
import dynamics

__author__ = 'mkompan'

import methods.sd_tools_graphine as sd_tools
import graphine
import sys
import polynomial
from polynomial import sd_lib, pole_extractor, formatter
from polynomial.polynomial_product import PolynomialProduct

use_eqs = False
#use_eqs = True

graph = graphine.Graph.fromStr(sys.argv[1])
graph._subgraphs_as_line_ids = []
internal_edges = sd_tools.internal_edges_dict(graph)
cons = conserv.Conservations(internal_edges)
if use_eqs :
    eqs = sd_tools.find_eq(cons)
else:
    eqs = dict()
print eqs
cons = sd_tools.apply_eq(cons, eqs)
graph._cons = cons
graph._qi, graph._qi2l = sd_tools.qi_lambda(cons, eqs)
print graph._qi
D = sd_tools.gendet(graph)



D_ = sd_tools.gendet(graph)

D = polynomial.poly(map(lambda x:(1,x), D_), degree=(-3,1)).toPolyProd()
print D
delta = polynomial.poly(map(lambda x: (1,(x,)), D.getVarsIndexes()))
print delta

tree = sd_tools.gen_speer_tree(graph)

for sector in dynamics.xTreeElement2(tree):
    print sector
    expr = sd_lib.sectorDiagram(D, sector, delta_arg=delta)[0][0].simplify()
    print expr

    print isinstance(expr, PolynomialProduct)
    extracted = pole_extractor.extract_poles_and_eps_series(expr, 1)
    formatted_dict = formatter.formatPoleExtracting(extracted)
    print formatted_dict.keys()
    for i in formatted_dict.keys():
        print i, len(formatted_dict[i]), type(formatted_dict[i])
        if i == -2:
            print formatted_dict[i]
