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

