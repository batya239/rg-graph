#!/usr/bin/python
# -*- coding: utf8
import itertools

__author__ = 'mkompan'

import comb


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
        for subgraph2_edges in merged:
            if len(set(subgraph_edges) & set(subgraph2_edges)) != 0:
                to_merge.append(subgraph2_edges)
            else:
                merged_.append(subgraph2_edges)
        merged_subgraph = set(subgraph_edges)
        for subgraph_edges in to_merge:
            merged_subgraph = merged_subgraph|set(subgraph_edges)
        merged_.append(list(merged_subgraph))
        merged = merged_

    return merged

def find_max_non_covered_subgraphs(subgraphs_with_index, graph):
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
    if union == set(internal_edges_dict(graph).keys()):
        return result[:-1]
    else:
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
    result = set(graph_qi.keys())
    for subgraph in subgraphs:
        result -= set(internal_edges_dict(subgraph).keys())
    return list(result)
