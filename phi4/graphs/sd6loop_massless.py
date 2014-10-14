#!/usr/bin/python
# -*- coding: utf8
import os
import conserv
from graph_state_builder_static import gs_builder
import methods.sd_tools_graphine as sd_tools
import graphine
import sys
import polynomial
from polynomial import sd_lib

__author__ = 'mkompan'


use_eqs = False
#use_eqs = True
graph = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))
print str(graph), gs_builder.graph_state_from_str(sys.argv[1])
eps_order = int(sys.argv[2])
graph._subgraphs_as_line_ids = []
space_dim = 4

if graph.external_edges_count == 2:

    internal_edges_c = sd_tools.internal_edges_dict(graph)
    internal_edges_c['special_edge_for_C'] = list(graph.get_bound_vertices())

    conservations_c1 = conserv.Conservations(internal_edges_c)
    if use_eqs:
        eqs = sd_tools.find_eq(conservations_c1)
    else:
        eqs = dict()
    conservations_c = sd_tools.apply_eq(conservations_c1, eqs)
    graph._cons = conservations_c
    graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations_c, eqs)
    print graph._qi

    C_ = sd_tools.gendet(graph, n=graph.loops_count + 1)
    internal_edges = sd_tools.internal_edges_dict(graph)
    cons = conserv.Conservations(internal_edges)
    cons = sd_tools.apply_eq(cons, eqs)
    graph._cons = cons

    print internal_edges
    A = len(graph.internal_edges)
    L = graph.loops_count
    D_ = sd_tools.gendet(graph)
    c_pow, d_pow = ((-A + space_dim/2*L , -L), (A - space_dim/2*(L+1), L+1))
    print c_pow, d_pow
    D = polynomial.poly(map(lambda x: (1, x), D_), degree=d_pow)
    C = polynomial.poly(map(lambda x: (1, x), C_), degree=c_pow).toPolyProd()
    expr = C * D
    graph._cons = conservations_c
else:
    raise NotImplementedError("p-integrals only")

print "len(C) = ", len(C_)
print "len(D) = ", len(D_)
print expr

delta = polynomial.poly(map(lambda x: (1, (x,)), D.getVarsIndexes()))


tree = sd_tools.gen_speer_tree(graph, graph.loops_count+1, symmetries=True, skip_bad_branches=True)

dir = os.path.join("sd6loop_massless/", str(graph))
try:
    os.makedirs(dir)
except OSError:
    pass

print "sectors done, count =", len([x for x in sd_tools.xMSNTreeElement2(tree, debug=False)])

#print expr

for functions_file in sd_tools.generate_func_files(tree, lambda x: sd_lib.sectorDiagram(expr, x, delta_arg=delta)[0][0].simplify(), eps_order):
    print os.path.join(dir, "%s.c" % functions_file.get_file_name(str(graph))), functions_file.file_info, len(functions_file.functions), functions_file.functions_count
    f = open(os.path.join(dir, "%s.c" % functions_file.get_file_name(str(graph))), "w")
    f.write(functions_file.get_c_file())
    f.close()
    f = open(os.path.join(dir, "%s.h" % functions_file.get_file_name(str(graph))), "w")
    f.write(functions_file.get_h_file())
    f.close()
