import re
import sys
import conserv

from graphine import filters
import phi4.ir_uv as ir_uv

import graphine
import methods.sd_tools_graphine as sd_tools
import dynamics

#e12-23-4-45-5-e-
#e12-23-3-e-
#e12-33-45-6-57-7-e7--
#e12-34-35-e-55--
#e12-34-56-e7-55--77--


graph = graphine.Graph.fromStr(sys.argv[1])
internal_edges_c = sd_tools.internal_edges_dict(graph)
print graph.allEdges()
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

print sd_tools.find_max_non_overlapping_subgraphs(subgraphsUV)


print
print

if len(graph.externalEdges()) == 2:
    internal_edges_c['special_edge_for_C'] = list(graph.getBoundVertexes())

conservations_c1 = conserv.Conservations(internal_edges_c)
eqs = sd_tools.find_eq(conservations_c1)
conservations_c = sd_tools.apply_eq(conservations_c1, eqs)
graph._cons = conservations_c
print conservations_c
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


class Tree(object):
    def __init__(self, node, parents):
        self.node = node
        self.parents = parents
        self.branches = list()

    def setBranches(self, branches):
        self.branches = list()
        for branch in branches:
            if isinstance(branch, Tree):
                self.branches.append(branch)
            else:
                if self.node is None:
                    self.branches.append(Tree(branch, self.parents))
                else:
                    self.branches.append(Tree(branch, self.parents + [self.node]))

overlapping_subgraphs = sd_tools.find_max_non_overlapping_subgraphs(subgraphsUV)
variables = sd_tools.find_excluded_edge_ids(graph._qi, overlapping_subgraphs) + ['a%s' % x._sd_idx for x in overlapping_subgraphs]

homogeneity = graph.batchShrinkToPoint(overlapping_subgraphs).getLoopsCount()
print homogeneity


def is_denied_by_conservations(vars, conservations):
    var_set = set(vars)
    for cons in conservations:
        if cons.issubset(var_set):
            return True
    return False


def is_valid_var(var, parents, conservations):
    if var in parents:
        return False
    else:
        return not is_denied_by_conservations(parents+[var], conservations)


def safe_subgraph_ids(primary_vars, conservations, subgraphs):
    subgraph_ids = [x._sd_idx for x in subgraphs]
    result = list()
    for id in subgraph_ids:
        for cons in conservations:
            if cons.issubset(set(primary_vars+["a%s"%id])):
                result.append(id)
                break
    return result


def remove_subgraph_by_ids(subgraphs, ids):
    result = list()
    subgraph_by_id = dict(map(lambda x: (x._sd_idx,  x), subgraphs))
    subgraph_edges = dict(map(lambda x: (x._sd_idx, frozenset(sd_tools.internal_edges_dict(x).keys())), subgraphs))
    for i in subgraph_by_id.keys():
        subgraph = subgraph_by_id[i]
        if i not in ids:
            for id in ids:
                if subgraph_edges[i].issubset(subgraph_edges[id]):
                    subgraph._sd_domain.append(id)
            result.append(subgraph)
    return result


def get_subgraph_id(var):
    if isinstance(var, str):
        regex = re.match('a(\d+)', var)
        if regex is not None:
            return int(regex.groups()[0])
    return None


def add_subgraph_branches(tree, graph, subgraphs, conservations):
#    domains = sd_tools.subgraph_domains(subgraphs)
#    overlapping_subgraphs = sd_tools.find_max_non_overlapping_subgraphs(domains[0] if len(domains) > 0 else [])
    subgraphs_to_decouple = sd_tools.find_max_non_covered_subgraphs(subgraphs, graph)
    variables = sd_tools.find_excluded_edge_ids(graph._qi, subgraphs_to_decouple) + ['a%s' % x._sd_idx for x in subgraphs_to_decouple]
    homogeneity = graph.batchShrinkToPoint(sd_tools.merge_overlapping_subgraphs(subgraphs_to_decouple)).getLoopsCount()
    assert homogeneity != 0
    print "add_subgraph_branches", tree.node, tree.parents, map(lambda x: x._sd_idx, subgraphs_to_decouple), variables, homogeneity
    add_branches(tree, variables, conservations, graph, subgraphs, depth=homogeneity)


def remove_subgraphs_from_conservations(conservations, subgraph_ids):
    subgraph_vars = set(["a%s" % x for x in subgraph_ids])
    conservations_ = list()
    for cons in conservations:
        if len(cons & subgraph_vars) == 0:
            conservations_.append(cons)
    return set(conservations_)


def add_branches(tree, variables, conservations, graph, subgraphs, depth):
    if depth == 0:
        return
    else:
        print "node", tree.parents, tree.node, len(conservations), [x._sd_idx for x in subgraphs],
        branches = list()
        if tree.node is None:
            parents_ = tree.parents
        else:
            parents_ = tree.parents+[tree.node]
        for var in variables:
            #print var, tree.parents, is_valid_var(var, parents_, conservations)
            if is_valid_var(var, parents_, conservations):
                branches.append(var)
        print branches
        if len(branches) == 1:
            raise ValueError("%s, %s , %s" % (branches, [x for x in dynamics.xTreeElement(tree)], parents_))
        elif len(branches) != 0:
            tree.setBranches(branches)
#        print tree.node, branches
        for branch in tree.branches:
            subgraph_id = get_subgraph_id(branch.node)
            if subgraph_id is not None:
                subgraphs_ = remove_subgraph_by_ids(subgraphs, [subgraph_id])
                conservations_ = remove_subgraphs_from_conservations(conservations, [subgraph_id])
                add_subgraph_branches(branch, graph, subgraphs_, conservations_)
            else:
                subgraph_ids_to_remove = safe_subgraph_ids(branch.parents+[branch.node], conservations, subgraphs)
                if len(subgraph_ids_to_remove) != 0:
                    subgraphs_ = remove_subgraph_by_ids(subgraphs, subgraph_ids_to_remove)
                    conservations_ = remove_subgraphs_from_conservations(conservations, subgraph_ids_to_remove)
                    add_subgraph_branches(branch, graph, subgraphs_, conservations_)
                else:
                    add_branches(branch, variables, conservations, graph, subgraphs, depth-1)


def gen_sdt_tree(graph, subgraphs, conservations):
    sdt_tree = Tree(None, [])
    subgraphs_ = subgraphs
    add_subgraph_branches(sdt_tree, graph, subgraphs, conservations)
    return sdt_tree

tree = gen_sdt_tree(graph, subgraphsUV, conservations_for_sd)

for x in dynamics.xTreeElement2(tree):
    print x
