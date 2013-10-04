__author__ = 'gleb'

import copy
import itertools
import polynomial
import polynomial.sd_lib as sd_lib
from . import adjacency_combinatorics as ac

import nickel
import graph_state


def sectors(c_laws, loops, variable_list):
    """
    :param c_laws:
    :param loops:
    :param variable_list: is a list of variables in Feynman's interpretation integrand
    :return:
    """

    sb = variable_list
    perms = list(itertools.permutations(sb, loops))

    result = []
    sector = []

    for p in perms:
        for edge in p:
            tmp = (edge, [x for x in sb if x != edge])
            sb = [x for x in sb if x != edge]
            sector.append(copy.deepcopy(tmp))
        result.append(copy.deepcopy(sector))
        del sector[:]
        sb = variable_list

    tmp = []
    tmp2 = []
    nums_to_remove = set([])
    for num, sector in enumerate(result):
        for stage, dec in enumerate(sector):
            tmp.append(dec[0])
            for law in c_laws:
                if set(tmp).issuperset(set(law)):
                    for s in result:
                        for i in list(xrange(0, stage)):
                            tmp2.append(s[i][0])
                        if set(tmp2).issuperset(set(tmp[0:stage])):
                            for i in list(xrange(stage, len(s))):
                                if tmp[stage] in s[i][1]:
                                    s[i][1].remove(tmp[stage])
                        del tmp2[:]
                    nums_to_remove.add(num)
        del tmp[:]

    for n in sorted(list(nums_to_remove), reverse=True):
        result.pop(n)

    for sector in result:
        for dec in reversed(sector):
            if len(dec[1]) == 0:
                sector.remove(dec)

    return result


def remove_symmetrical_sectors(NDiag, all_sectors):
    """
    :param NDiag:
    :param all_sectors:
    :return:
    """
    result = []

    d = copy.deepcopy(NDiag)

    for edge in d:
        if len(edge) == 2:
            edge.append(0)

    test_diagrams = []
    for _ in itertools.repeat(None, len(all_sectors)):
        test_diagrams.append(copy.deepcopy(d))

    for sec_num, sector in enumerate(all_sectors):
        for dec_num, dec in enumerate(sector):
            test_diagrams[sec_num][dec[0]][2] = dec_num + 1

    labels = []
    for d in test_diagrams:
        labels.append(str(graph_state.GraphState(map(lambda x: graph_state.Edge(x[0:2], colors=x[2]), d))))

    for num, label in enumerate(labels):
        if not label in labels[0:num]:
            result.append((labels.count(label), all_sectors[num]))

    return result


def decompose_integrand(f_repr, g_info, wanted_sectors=()):
    """
    """

    Integrand = f_repr['integrand']
    Delta_argument = f_repr['d-func argument']

    if 0 == len(wanted_sectors):
        all_sectors = sectors(g_info['conservation laws'], g_info['loops'], f_repr['variable list'])
        ns_sectors = remove_symmetrical_sectors(g_info['adjacency list'], all_sectors)
    else:
        ns_sectors = map(lambda x: (1, list(x)), wanted_sectors)

    result = []
    for sector in ns_sectors:
        res = sd_lib.sectorDiagram(Integrand, sector[1], Delta_argument)[0][0]
        coefficient = polynomial.poly([(1, []), ], degree=1)
        coefficient.c *= sector[0]
        res *= coefficient.toPolyProd()
        res = res.simplify()
        result.append(res)

    decomposition_info = dict()
    decomposition_info['integrand'] = Integrand
    decomposition_info['d-func argument'] = Delta_argument
    decomposition_info['sectors'] = ns_sectors
    decomposition_info['sector expressions'] = result

    return decomposition_info


def rename_sector_vars(polypr, sector):
    """
    """
    renaming_dict = dict()
    last_var = 1

    for dec in sector:
        renaming_dict[dec[0]] = last_var
        last_var += 1

    for dec in reversed(sector):
        for v in dec[1]:
            if not v in renaming_dict.keys():
                renaming_dict[v] = last_var
                last_var += 1

    result = copy.deepcopy(polypr)
    for poly in result.polynomials:
        for monomial in poly.monomials:
            for k in monomial.vars.keys():
                monomial.vars[renaming_dict[k]] = monomial.vars.pop(k)

    return result
