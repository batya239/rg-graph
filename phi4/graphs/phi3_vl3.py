#!/usr/bin/python
# -*- coding: utf8
import os

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
if use_eqs:
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

D = polynomial.poly(map(lambda x: (1, x), D_), degree=(-3, 1)).toPolyProd()
#print D
delta = polynomial.poly(map(lambda x: (1, (x,)), D.getVarsIndexes()))
#print delta

tree = sd_tools.gen_speer_tree(graph)

dir = os.path.join("sample_extraction/", str(graph))
try:
    os.makedirs(dir)
except OSError:
    pass

print "sectors done"

for functions_file in sd_tools.generate_func_files(tree, lambda x: sd_lib.sectorDiagram(D, x, delta_arg=delta)[0][0].simplify()):
    print os.path.join(dir, "%s.c" % functions_file.get_file_name(str(graph))), functions_file.file_info, len(functions_file.functions), functions_file.functions_count
    f = open(os.path.join(dir, "%s.c" % functions_file.get_file_name(str(graph))), "w")
    f.write(functions_file.get_c_file())
    f.close()
    f = open(os.path.join(dir, "%s.h" % functions_file.get_file_name(str(graph))), "w")
    f.write(functions_file.get_h_file())
    f.close()
