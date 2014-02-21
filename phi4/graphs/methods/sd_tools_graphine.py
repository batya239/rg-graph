#!/usr/bin/python
# -*- coding: utf8
import collections
import itertools
import re
from polynomial.polynomial_product import PolynomialProduct
import polynomial.sd_lib as sd_lib
from polynomial import pole_extractor, formatter

__author__ = 'mkompan'

import comb
import copy


def xTreeElement(tree, parents=list()):
    parents_ = copy.copy(parents)
    if tree.node is not None:
        parents_.append(tree.node)
    if len(tree.branches) == 0:
        yield parents_
    else:
        for branch in tree.branches:
            for elem in xTreeElement(branch, parents_):
                yield elem


def xTreeElement2(tree, parents=list(), varMap=dict(), debug=False):
    if len(tree.branches) == 0:
        yield parents
    else:
        branchIds = [x if x not in varMap else varMap[x] for x in map(lambda x: x.node, tree.branches)]
        for branch in tree.branches:
            branchIds_ = copy.copy(branchIds)
            branchIds_.remove(branch.node)
            parents_ = copy.copy(parents) + [(branch.node if branch.node not in varMap else varMap[branch.node],
                                              branchIds_)]
            for elem in xTreeElement2(branch, parents_, varMap):
                yield elem
            if tree.node is None and debug:
                print
        if debug:
            print


def internal_edges_dict(graph):
    return dict(map(lambda x: (x.edge_id, x.nodes), graph.internalEdges()))


def find_eq(conservations):
    def merge_eqs(equations, equation):
        new_equation = set(equation)
        merged_equations = list()
        for i in range(len(equations)):
            current_equation = equations[i]
            if len(current_equation & new_equation) == 0:
                merged_equations.append(current_equation)
            else:
                new_equation = new_equation | current_equation
        merged_equations.append(new_equation)
        return merged_equations

    res = dict()
    eqs = list()
    for conservation in conservations:
        if len(conservation) == 2:
            eqs = merge_eqs(eqs, conservation)
    for eq in eqs:
        eq_ = list(eq)
        for var in eq_[1:]:
            res[var] = eq_[0]
    return res


def apply_eq(conservations, equations):
    res = set()
    for current_conservation_ in conservations:
        current_conservation = set(current_conservation_)
        for eq in equations:
            if eq in current_conservation:
                if set([eq, equations[eq]]).issubset(current_conservation):
                    current_conservation = current_conservation - set([eq, equations[eq]])
                else:
                    current_conservation = (current_conservation - set([eq])) | set([equations[eq]])
        current_conservation = frozenset(current_conservation)
        if len(current_conservation) > 1:
            res = res | set([current_conservation])
    return res


def unique_ui(conservations, ui_to_remove=['special_edge_for_C']):
    res = set()
    for current_conservation in conservations:
        res = res | current_conservation
    res = res - set(ui_to_remove)
    return res


def qi_lambda(conservations, equations):
    qi = dict()
    qi2line = dict()
    for ui in unique_ui(conservations):
        qi[ui] = 1
        qi2line[ui] = [ui]
    for eq in equations:
        ui = equations[eq]
        if len(conservations) == 0:
            qi[ui] = 0
            qi2line[ui] = [ui]
        qi[ui] += 1
        qi2line[ui].append(eq)
    return qi, qi2line


def check_cons(term, conservations):
    """
    check if the combination of vars denied by conservation laws
    False -> Denied
    """
    res = True
    for conservation in conservations:
        if conservation.issubset(term):
            res = False
            break
    return res


def stretch_list(sector, graph, unique=False):
    """ generate list of strechs extracted in leading term by first pass of sector decomposition
    """

    stretch = []
    subs = graph._subgraphs_as_line_ids
    for j in range(len(subs)):
        si = len(set(sector) & set(subs[j])) - graph._subgraphs[j].getLoopsCount()
        stretch += ["a%s" % j] * si
    if unique:
        return list(set(stretch))
    else:
        return stretch


def gendet(graph, n=None):
    """
    generate feynman det for graph
    graph must have _qi2l, _cons, _subgraphs, _subgraphs_as_line_ids
    """
    if n is None:
        n_ = graph.getLoopsCount()
    else:
        n_ = n
    det = []
    for term in comb.xUniqueCombinations(graph._qi2l.keys(), n_):
        if check_cons(term, graph._cons):
            det.append(term + stretch_list(term, graph))
    return det


def find_conservations(D, all_vars):
    conservations = list()
    for i in range(1, len(all_vars)):
        for comb in itertools.combinations(all_vars, i):
            present = False
            for term in D:
                if set(comb).issubset(set(term)):
                    present = True
                    break
            if not present:
                valid = True
                for cons in conservations:
                    if set(cons).issubset(comb):
                        valid = False
                        break
                if valid:
                    conservations.append(frozenset(comb))
    return set(conservations)

#def subgraph_domains(subgraphs):
#    result = dict()
#    for subgraph in subgraphs:
#        if tuple(subgraph._sd_domain) not in result:
#            result[tuple(subgraph._sd_domain)] = [subgraph]
#        else:
#            result[tuple(subgraph._sd_domain)].append(subgraph)
#    return result.values()


def merge_overlapping_subgraphs(subgraphs):
    merged = list()
    for subgraph in subgraphs:
        subgraph_edges = subgraph.internalEdges()
        to_merge = list()
        merged_ = list()
        for subgraph2_edges, common_edges in merged:
            if len(set(subgraph_edges) & set(subgraph2_edges)) != 0:
                to_merge.append((subgraph2_edges, common_edges))
            else:
                merged_.append((subgraph2_edges, common_edges))
        merged_subgraph = set(subgraph_edges)
        common_edges = set(subgraph_edges)
        for subgraph_edges, common_edges_ in to_merge:
            merged_subgraph = merged_subgraph | set(subgraph_edges)
            common_edges = common_edges & set(common_edges_)
        merged_.append((list(merged_subgraph), list(common_edges)))
        merged = merged_
        #print "merge"
    #print subgraphs
    #print merged
    #print
    return merged


def find_max_non_covered_subgraphs(subgraphs_with_index, graph, parents):
    subgraphs_ = sorted(subgraphs_with_index, key=lambda x: len(x.internalEdges()), reverse=True)
    result = list()
    union = set()

    for subgraph1 in subgraphs_:
        covered = False
        internal_edges1 = frozenset(internal_edges_dict(subgraph1).keys())
        for subgraph2 in result:
            internal_edges2 = frozenset(internal_edges_dict(subgraph2).keys())
            #print internal_edges1, internal_edges2, internal_edges1.issubset(internal_edges2)
            if internal_edges1.issubset(internal_edges2):
                covered = True
                break
        if not covered:
            result.append(subgraph1)
            union = union | internal_edges1
            #print
            #print union
            #print
            #print set(internal_edges_dict(graph).keys())
            #print map(lambda x: internal_edges_dict(x).keys(), result)
    validated = False
    while not validated:
        validated = True
        #if len(result) != 1 and len(merge_overlapping_subgraphs(result)) == 1:
        #    result = result[:-1]
        #    validated = False
        if find_homogeneity(graph, result, parents) <= 0 and len(result) > 0:
            result = result[:-1]
            validated = False
            #print "mfncs", find_homogeneity(graph, result, parents), result, parents

    return result


def find_max_non_overlapping_subgraphs(subgraphs_with_index):
    def is_overlapping(subgraph1, subgraph2):
        return len(set(internal_edges_dict(subgraph1).keys()) & set(internal_edges_dict(subgraph2).keys())) != 0

    subgraphs_ = sorted(subgraphs_with_index, key=lambda x: len(x.internalEdges()), reverse=True)
    result = list()

    for subgraph1 in subgraphs_:
        overlapping = False
        for subgraph2 in result:
            if is_overlapping(subgraph1, subgraph2):
                overlapping = True
                break
        if not overlapping:
            result.append(subgraph1)

    return result


def find_excluded_edge_ids(graph_qi, subgraphs):
    merged = merge_overlapping_subgraphs(subgraphs)
    if len(merged) == 0:
        common_edges = list()
    else:
        common_edges = zip(*merged)[1]
    result = set(graph_qi.keys())
    for edges in common_edges:
        result -= set(map(lambda x: x.edge_id, edges))
        #print "excluded edges"
    #print list(result)
    return list(result)


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
        return not is_denied_by_conservations(parents + [var], conservations)


def safe_subgraph_ids(primary_vars, conservations, subgraphs):
    subgraph_ids = [x._sd_idx for x in subgraphs]
    result = list()
    for id in subgraph_ids:
        for cons in conservations:
            if cons.issubset(set(primary_vars + ["a%s" % id])):
                result.append(id)
                break
    return result


def remove_subgraph_by_ids(subgraphs, ids):
    result = list()
    subgraph_by_id = dict(map(lambda x: (x._sd_idx, x), subgraphs))
    subgraph_edges = dict(map(lambda x: (x._sd_idx, frozenset(internal_edges_dict(x).keys())), subgraphs))
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


def find_homogeneity(graph, subgraphs, parents):
    merged = merge_overlapping_subgraphs(subgraphs)
    if len(merged) == 0:
        common_edges = list()
    else:
        common_edges = zip(*merged)[1]
    return graph.batchShrinkToPoint(common_edges).getLoopsCount() - len(
        set(parents) & set(internal_edges_dict(graph.batchShrinkToPoint(common_edges)).keys()))


def add_subgraph_branches(tree, graph, subgraphs, conservations):
    parents = tree.parents + ([tree.node] if tree.node is not None else [])
    subgraphs_to_decouple = find_max_non_covered_subgraphs(subgraphs, graph, parents)
    variables = find_excluded_edge_ids(graph._qi, subgraphs_to_decouple) + ['a%s' % x._sd_idx for x in
                                                                            subgraphs_to_decouple]
    homogeneity = find_homogeneity(graph, subgraphs_to_decouple, parents)
    if homogeneity == 0:
        return
    else:
        print "add_subgraph_branches", tree.node, tree.parents, map(lambda x: x._sd_idx,
                                                                    subgraphs_to_decouple), variables, homogeneity
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
        add_subgraph_branches(tree, graph, subgraphs, conservations)
    else:
        print "node", tree.parents, tree.node, len(conservations), [x._sd_idx for x in subgraphs],
        branches = list()
        if tree.node is None:
            parents_ = tree.parents
        else:
            parents_ = tree.parents + [tree.node]
        for var in variables:
            #print var, tree.parents, is_valid_var(var, parents_, conservations)
            if is_valid_var(var, parents_, conservations):
                branches.append(var)
        print branches
        if len(branches) == 1:
            raise ValueError("%s, %s , %s" % (branches, [x for x in xTreeElement(tree)], parents_))
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
                subgraph_ids_to_remove = safe_subgraph_ids(branch.parents + [branch.node], conservations, subgraphs)
                if len(subgraph_ids_to_remove) != 0:
                    subgraphs_ = remove_subgraph_by_ids(subgraphs, subgraph_ids_to_remove)
                    conservations_ = remove_subgraphs_from_conservations(conservations, subgraph_ids_to_remove)
                    add_subgraph_branches(branch, graph, subgraphs_, conservations_)
                else:
                    add_branches(branch, variables, conservations, graph, subgraphs, depth - 1)


def gen_sdt_tree(graph, subgraphs, conservations):
    sdt_tree = Tree(None, [])
    add_subgraph_branches(sdt_tree, graph, subgraphs, conservations)
    return sdt_tree

#####################################################
#
#####################################################


def get_ui_count(variables):
    ui_count = reduce(lambda x, y: x + y, [1 if isinstance(x, long) else 0 for x in variables])
    return ui_count


def get_ui(variables):
    res = list()
    for var in variables:
        if isinstance(var, long):
            res.append(var)
    return res


def xCombinations_with_exceptions(seq, n, denied_combinations=list()):
    """Generator of all the n-element combinations of the given sequence.
    """
    if n == 0:
        yield seq[0:0]
    else:
        for i in range(len(seq)):
            for tail in xCombinations_with_exceptions(seq[:i] + seq[i + 1:], n - 1, denied_combinations):
                combination = seq[i:i + 1] + tail
                if not is_subset(combination, denied_combinations):
                #                    print combination, get_ui_count(combination), ui_count
                    yield combination


def check_zero(poly, variables):
    variables_ = frozenset(variables)
    return set([]) not in map(lambda x: variables_ & x.getVarsIndexes(), poly.monomials.keys())


def is_subset(combination, zeroes):
    combination_ = frozenset(combination)
    return True in map(lambda x: x.issuperset(combination_), zeroes)


def is_superset(combination, zeroes):
    combination_ = frozenset(combination)
    return True in map(lambda x: x.issubset(combination_), zeroes)


def find_zeroes(poly, denied_combinations):
    variables = frozenset(poly.getVarsIndexes())
    zeroes = list()
    for n in range(2, len(variables)):  ## +1?
        print n, zeroes
        for combination in xCombinations_with_exceptions(list(variables), n, denied_combinations + zeroes):
            if not is_superset(combination, zeroes):
                if check_zero(poly, combination):
                    zeroes.append(frozenset(combination))
    print "zzz", zeroes
    return zeroes


def find_min_zero(poly, denied_combinations):
    variables = frozenset(poly.getVarsIndexes())
    zeroes = list()
    for n in range(2, len(variables)):  ## +1?
        print n, zeroes
        for combination in xCombinations_with_exceptions(list(variables), n, denied_combinations + zeroes):
            if not is_superset(combination, zeroes):
                if check_zero(poly, combination):
                    zeroes.append(frozenset(combination))
                    print "zzz", zeroes
                    return zeroes
    print "zzz", zeroes
    return zeroes

#def find_max_zero(poly, ui_count):
#    variables = poly.getVarsIndexes()
#    zeroes = list()
#    for n in range(len(variables)-1, 1, -1):  ## +1?
#        for combination in xCombinations_with_exceptions(list(variables), n, ui_count):
#            if check_zero(poly, combination):
#                if not is_superset(zeroes, combination):
#                    zeroes.append(frozenset(combination))
#                    return zeroes
#    return zeroes


def non_factorized_part(poly):
    if isinstance(poly, PolynomialProduct):
        polyprod = poly.simplify()
    else:
        polyprod = poly.toPolyProd().simplify()

    for poly_ in polyprod.polynomials:
        if len(poly_.monomials) > 1:
            return poly_


def add_adoptive_branches(tree, poly, denied_combinations=list(), parents=[]):
#    zeroes = sorted(find_zeroes(poly, denied_combinations), key=len, reverse=True)
    zeroes = find_min_zero(poly, denied_combinations)
    print parents, tree.node
    print  zeroes
    if len(zeroes) != 0:
        tree.setBranches(zeroes[0])
        for i in range(len(tree.branches)):
            branch = tree.branches[i]
            poly_ = sd_lib.sectorPoly(poly,
                                      [[branch.node, map(lambda x: x.node, tree.branches[:i] + tree.branches[i + 1:])]])
            #            print non_factorized_part(poly_)
            add_adoptive_branches(branch, non_factorized_part(poly_), denied_combinations,
                                  parents=parents + [(branch.node, (tuple(zeroes)))])


def gen_adoptive_tree(poly):
    tree = Tree(None, [])
    variables = poly.getVarsIndexes()
    add_adoptive_branches(tree, poly, [frozenset(get_ui(variables))], parents=list())
    return tree


def add_speer_branches(tree, variables, conservations, parents=list(), depth=0):
#    print parents, depth
    if depth == 0:
        return
    else:
        parent_main_vars = map(lambda x: x[0], parents)
        branches = list()
        for variable in variables:
            if variable in parent_main_vars:
                continue
            if not is_superset(parent_main_vars + [variable], conservations):
                branches.append(variable)
                #        print parent_main_vars, branches
        if len(branches) == 0:
            return
        elif len(branches) == 1:
            raise ValueError("parents: %s, branches %s" % (parents, branches))
        else:
            tree.setBranches(branches)
            for branch in tree.branches:
                add_speer_branches(branch, variables, conservations, parents=parents + [(branch.node, tuple(branches))],
                                   depth=depth - 1)


def gen_speer_tree(graph, depth=None):
    tree = Tree(None, [])
    variables = graph._qi.keys()
    if depth is None:
        add_speer_branches(tree, variables, graph._cons, parents=list(), depth=graph.getLoopsCount())
    else:
        add_speer_branches(tree, variables, graph._cons, parents=list(), depth=depth)
    return tree


resultingFunctionTemplate = """
double func_t_{fileIdx}(double k[DIMENSION])
{{
double f=0;
{resultingFunctions}
return f;
}}
"""

functionBodyTemplate = """
{comments}
{vars}
double f=0;
{expr}
return f;
"""

functionTemplate = """
double func{idx}_t_{fileIdx}(double k[DIMENSION])
{{
{functionBody}
}}
"""

functionsCodeTemplate = """
#include <math.h>
#define DIMENSION {dims}

{functions}

{resultingFunction}
"""

headerCodeTemplate = """
#include <math.h>
#define DIMENSION {dims}

double func_t_{fileIdx}(double k[DIMENSION]);
"""


def generate_function_body(expr_string, variables_list, comments=""):
    vars_string = ""
    for i in range(len(variables_list)):
        variable = variables_list[i]
        vars_string += "double %s=k[%s];\n" % (variable, i)
    return functionBodyTemplate.format(comments=comments,
                                       vars=vars_string,
                                       expr="f += %s;" % expr_string)


class FunctionsFile(object):
    def __init__(self, file_idx):
        self.file_idx = file_idx
        self.file_info = None
        self.functions = ""
        self.functions_count = 0

    def add_function(self, function_body):
        self.functions += functionTemplate.format(idx=self.functions_count,
                                                  fileIdx=self.file_idx,
                                                  functionBody=function_body)
        self.functions_count += 1

    def set_file_info(self, file_info):
        self.file_info = file_info

    def __len__(self):
        return len(self.functions)

    def _resulting_function(self):
        function_body = ""
        for i in range(self.functions_count):
            function_body += "f+=func{idx}_t_{fileIdx}(k);\n".format(fileIdx=self.file_idx, idx=i)
        return resultingFunctionTemplate.format(fileIdx=self.file_idx,
                                                resultingFunctions=function_body)

    def get_c_file(self):
        return functionsCodeTemplate.format(dims=self.file_info.dimension,
                                            functions=self.functions,
                                            resultingFunction=self._resulting_function())

    def get_h_file(self):
        return headerCodeTemplate.format(dims=self.file_info.dimension,
                                         fileIdx=self.file_idx)

    def get_file_name(self, prefix):
        return "%s_func_%s_V%s_E%s" % (prefix,
                                       self.file_idx,
                                       self.file_info.dimension,
                                       self.file_info.eps_order)

funcFileInfo = collections.namedtuple("funcFileInfo", ["eps_order", "dimension"])

maxFunctionLength = 1000000


def generate_func_files(tree, generate_expr_for_sector, eps_order=0):
    files = collections.defaultdict(lambda: FunctionsFile(0))
    for sector in xTreeElement2(tree):
        expr = generate_expr_for_sector(sector)
#        print sector
#        print expr
        #print eps_order
        extracted = pole_extractor.extract_poles_and_eps_series(expr, eps_order)
        #print extracted
        #print
        formatted_dict = formatter.formatPoleExtracting(extracted)
        for eps_order_ in formatted_dict:
            for expr, variables in formatted_dict[eps_order_]:
                file_info = funcFileInfo(eps_order_, len(variables))
                function_file = files[file_info]
                function_file.add_function(generate_function_body(expr, variables, "// sector: %s" % sector))

                if len(function_file) > maxFunctionLength:
                    function_file.set_file_info(file_info)
                    files[file_info] = FunctionsFile(function_file.file_idx + 1)
                    yield function_file

    for file_info, function_file in files.items():
        if len(function_file) != 0:
            function_file.set_file_info(file_info)
            yield function_file




        #        yield sector, generate_expr_for_sector(sector)