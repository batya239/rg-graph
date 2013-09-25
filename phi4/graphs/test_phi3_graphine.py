import sys
import conserv

from graphine import filters
import phi4.ir_uv as ir_uv

import graphine
import methods.sd_tools_graphine as sd_tools


graph = graphine.Graph.fromStr(sys.argv[1])
internal_edges_c = sd_tools.internal_edges_dict(graph)
print graph.allEdges()
print internal_edges_c
print graph.getBoundVertexes()
if len(graph.externalEdges()) == 2:
    internal_edges_c['special_edge_for_C'] = list(graph.getBoundVertexes())


conservations_c1 = conserv.Conservations(internal_edges_c)
eqs = sd_tools.find_eq(conservations_c1)
conservations_c = sd_tools.apply_eq(conservations_c1, eqs)
graph._cons = conservations_c
print conservations_c
graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations_c, eqs)


ir_uv.spaceDim = 6
uv = ir_uv.UVRelevanceCondition()

subgraphUVFilters = (filters.oneIrreducible
                     + filters.noTadpoles
                     + filters.vertexIrreducible
                     + filters.isRelevant(uv))

subgraphsUV = [subg for subg in
               graph.xRelevantSubGraphs(subgraphUVFilters, graphine.Representator.asGraph)]

graph._subgraphs = subgraphsUV
graph._subgraphs_as_line_ids = map(lambda x: sd_tools.internal_edges_dict(x).keys(), subgraphsUV)

for subgraph in subgraphsUV:
    print subgraph
    print sd_tools.internal_edges_dict(subgraph).keys()


if len(graph.externalEdges()) == 2:
    C = sd_tools.gendet(graph, n=graph.getLoopsCount()+1)
else:
    C = None
print C

if len(graph.externalEdges()) == 2:
    internal_edges = sd_tools.internal_edges_dict(graph)
    cons = conserv.Conservations(internal_edges)
    cons = sd_tools.apply_eq(cons, eqs)
    graph._cons = cons
D = sd_tools.gendet(graph)
print D

allVars = sorted(reduce(lambda x, y: set(x) | set(y), D))
conservations_for_sd = sd_tools.find_conservations(D, allVars)

print conservations_for_sd

