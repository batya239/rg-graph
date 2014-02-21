#!/usr/bin/python
# -*- coding: utf8
import os

import conserv

__author__ = 'mkompan'

from graph_state_builder_static import gs_builder
import methods.sd_tools_graphine as sd_tools
import graphine
import sys
import polynomial
from polynomial import sd_lib
from polynomial.polynomial_product import PolynomialProduct

use_eqs = False
#use_eqs = True

graph = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))
eps_order = int(sys.argv[2])
graph._subgraphs_as_line_ids = []
if graph.externalEdgesCount() != 2:
    raise NotImplementedError("p-integrals only")
internal_edges_c = sd_tools.internal_edges_dict(graph)
internal_edges_c['special_edge_for_C'] = list(graph.getBoundVertexes())

conservations_c1 = conserv.Conservations(internal_edges_c)
if use_eqs:
    eqs = sd_tools.find_eq(conservations_c1)
else:
    eqs = dict()
print eqs
conservations_c = sd_tools.apply_eq(conservations_c1, eqs)
graph._cons = conservations_c
#print conservations_c
graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations_c, eqs)
print graph._qi

C_ = sd_tools.gendet(graph, n=graph.getLoopsCount() + 1)


internal_edges = sd_tools.internal_edges_dict(graph)
cons = conserv.Conservations(internal_edges)
cons = sd_tools.apply_eq(cons, eqs)
graph._cons = cons

print internal_edges

#internal_edges = sd_tools.internal_edges_dict(graph)
#cons = conserv.Conservations(internal_edges)
#cons = sd_tools.apply_eq(cons, eqs)
#graph._cons = cons
#graph._qi, graph._qi2l = sd_tools.qi_lambda(cons, eqs)
#print graph._qi
#D = sd_tools.gendet(graph)
A = len(graph.internalEdges())
L = graph.getLoopsCount()
D_ = sd_tools.gendet(graph)


space_dim = 4

print C_ # 1 = (1,0)
print D_ # -d/2-1 =(-3,1) (d=4-2*e)

D = polynomial.poly(map(lambda x: (1, x), D_), degree=(-space_dim/2-1, 1))
C = polynomial.poly(map(lambda x: (1, x), C_), degree=(1, 0)).toPolyProd()
expr = C * D
#print D
delta = polynomial.poly(map(lambda x: (1, (x,)), D.getVarsIndexes()))
#print delta

#tree = sd_tools.gen_speer_tree(graph)
#graph._cons = conservations_c
tree = sd_tools.gen_speer_tree(graph, graph.getLoopsCount()+1)

dir = os.path.join("sd6loop/", str(graph))
try:
    os.makedirs(dir)
except OSError:
    pass

print "sectors done"

print expr
#print eps_order
for functions_file in sd_tools.generate_func_files(tree, lambda x: sd_lib.sectorDiagram(expr, x, delta_arg=delta)[0][0].simplify(), eps_order):
    print os.path.join(dir, "%s.c" % functions_file.get_file_name(str(graph))), functions_file.file_info, len(functions_file.functions), functions_file.functions_count
    f = open(os.path.join(dir, "%s.c" % functions_file.get_file_name(str(graph))), "w")
    f.write(functions_file.get_c_file())
    f.close()
    f = open(os.path.join(dir, "%s.h" % functions_file.get_file_name(str(graph))), "w")
    f.write(functions_file.get_h_file())
    f.close()
