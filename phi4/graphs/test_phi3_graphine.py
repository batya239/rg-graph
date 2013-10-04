import sys

from graphine import filters
import phi4.ir_uv as ir_uv
import graphine
import polynomial
import polynomial.sd_lib as sd_lib
import polynomial.multiindex as multiindex

import conserv

import methods.sd_tools_graphine as sd_tools
import dynamics


#e12-23-4-45-5-e-
#e12-23-3-e-
#e12-33-45-6-57-7-e7--
#e12-34-35-e-55--
#e12-34-56-e7-55--77--


graph = graphine.Graph.fromStr(sys.argv[1])
internal_edges_c = sd_tools.internal_edges_dict(graph)
print internal_edges_c


#ir_uv.const.spaceDim = 6
uv = ir_uv.UVRelevanceCondition(6)

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isRelevant(uv))

subgraphsUV = [subg for subg in
               graph.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asGraph)]

graph._subgraphs = subgraphsUV
graph._subgraphs_as_line_ids = map(lambda x: sd_tools.internal_edges_dict(x).keys(), subgraphsUV)

for i in range(len(subgraphsUV)):
    subgraph = subgraphsUV[i]
    print i, sd_tools.internal_edges_dict(subgraph).keys()
    subgraph._sd_idx = i
    subgraph._sd_domain = list()

if len(graph.externalEdges()) == 2:
    internal_edges_c['special_edge_for_C'] = list(graph.getBoundVertexes())

conservations_c1 = conserv.Conservations(internal_edges_c)
eqs = sd_tools.find_eq(conservations_c1)
conservations_c = sd_tools.apply_eq(conservations_c1, eqs)
graph._cons = conservations_c
#print conservations_c
graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations_c, eqs)
print graph._qi

if len(graph.externalEdges()) == 2:
    C = sd_tools.gendet(graph, n=graph.getLoopsCount() + 1)
else:
    C = None

if len(graph.externalEdges()) == 2:
    internal_edges = sd_tools.internal_edges_dict(graph)
    cons = conserv.Conservations(internal_edges)
    cons = sd_tools.apply_eq(cons, eqs)
    graph._cons = cons
D = sd_tools.gendet(graph)
#print C
print D

allVars = sorted(reduce(lambda x, y: set(x) | set(y), D))
conservations_for_sd = sd_tools.find_conservations(D, allVars)

print
for x in conservations_for_sd:
    print list(x)
print


tree = sd_tools.gen_sdt_tree(graph, subgraphsUV, conservations_for_sd)

D_polyprod = polynomial.poly(map(lambda x: (1, x), D)).toPolyProd()
delta_arg = polynomial.poly(map(lambda x: (1, [x]), graph._qi.keys()))


def check_decomposition(expr):
    for poly in expr.polynomials:
        if len(poly.monomials) == 1:
            continue
        else:
            if multiindex.CONST not in poly.monomials:
                return False
    return True

print
print "Total number of sectors = ", len([x for x in dynamics.xTreeElement2(tree)])
print
count = 0
for sector in dynamics.xTreeElement2(tree):
    D_poly_ = sd_lib.sectorDiagram(D_polyprod, sector, delta_arg, remove_delta=False)
#    print D_poly_
    assert len(D_poly_) == 2, len(D_poly_)
    assert len(D_poly_[0]) == 1, len(D_poly_[0])
    d_simplified = D_poly_[0][0].simplify()
    count += 1
    if count % 100 == 0:
        sys.stdout.write("\r  %s... " % count)
        sys.stdout.flush()

    if not check_decomposition(d_simplified):
        print sector, d_simplified
        print d_simplified.set0toVar(7L).set0toVar(8L)
        #for i in range(1,len(sector)):
        #    D_poly_ = sd_lib.sectorDiagram(D_polyprod, sector[:i], delta_arg, remove_delta=False)[0][0].simplify()
        #    print i, D_poly_
print