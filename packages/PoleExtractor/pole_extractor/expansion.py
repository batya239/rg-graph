__author__ = 'gleb'

import copy
import itertools
import polynomial
import math


def merge_map(func, lst):
    tmp = map(func, lst)
    result = []
    while tmp:
        result.extend(tmp.pop(0))
    return result


def ac_principal_part(polyprod, pole_var, var_degree_a, var_degree_b):
    """
    part of analytical continuation function. returns 1st of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests
    result = dict()
    poly_list = [polyprod, ]

    for _ in itertools.repeat(None, -var_degree_a - 1):
        poly_list = merge_map(lambda x: x.diff(pole_var), poly_list)

    coef = (math.factorial(-1 - var_degree_a) ** (-1)) * (var_degree_b ** (-1))
    coef_as_poly = polynomial.poly([(1, []), ], degree=1, c=coef)
    poly_list = map(lambda x: x.set0toVar(pole_var) * coef_as_poly.toPolyProd(), poly_list)

    result[-1] = poly_list
    return result


def ac_expansion_part(polyprod, pole_var, var_degree_a, var_degree_b, toIndex):
    """
    part of analytical continuation function. returns 2nd of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests
    result = dict()

    if var_degree_a > -2:
        result[0] = []
        return result

    for k in range(0, toIndex + 1):
        poly_list = [polyprod, ]
        coef_1 = ((-var_degree_b) ** k)
        result[k] = []

        for i in range(-var_degree_a - 1):
            coef_2 = (math.factorial(i) * (i + var_degree_a + 1) ** (k + 1)) ** (-1)
            coef_as_poly = polynomial.poly([(1, []), ], degree=1, c=coef_1 * coef_2)
            result[k].append(map(lambda x: x.set0toVar(pole_var) * coef_as_poly.toPolyProd(), poly_list))
            poly_list = merge_map(lambda x: x.diff(pole_var), poly_list)

    return result


def ac_stretched_part(polyprod, pole_var, var_degree_a, var_degree_b):
    """
    part of analytical continuation function. returns 3rd of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests

    result = dict()
    stretcher = 'a' + str(pole_var)
    poly_list = [polyprod.stretch(stretcher, [pole_var, ]), ]

    for _ in itertools.repeat(None, -var_degree_a):
        poly_list = merge_map(lambda x: x.diff(stretcher), poly_list)

    if var_degree_a <= -2:
        stretch_factor = polynomial.poly([(1, []), (-1, [stretcher, ])], degree=(-var_degree_a - 1, 0))
        poly_list = map(lambda x: x * stretch_factor, poly_list)

    p = polynomial.poly([(1, [pole_var, ]), ], degree=(var_degree_a, var_degree_b))
    poly_list = map(lambda x: x * p.toPolyProd(), poly_list)

    result[0] = poly_list
    return result


def analytical_continuation(polyprod, pole_var, var_degree_a, var_degree_b, toIndex):
    result = dict()

    res1 = ac_principal_part(polyprod, pole_var, var_degree_a, var_degree_b)
    res2 = ac_expansion_part(polyprod, pole_var, var_degree_a, var_degree_b, toIndex)
    res3 = ac_stretched_part(polyprod, pole_var, var_degree_a, var_degree_b)

    all_keys = set(res1.keys() + res2.keys() + res3.keys())

    for k in list(all_keys):
        result[k] = []
        if k in res1.keys():
            result[k] += res1[k]
        if k in res2.keys():
            result[k] += res2[k]
        if k in res3.keys():
            result[k] += res3[k]
    return result


def remove_pole(poly_prod):
    """
    Removes a factorised pole from poly_prod if there is one and returns pole and poly_prod without it separately.
    """
    #TODO: tests tests tests
    def stretched(poly, var_index):
        str_name = 'a' + str(var_index)
        if str_name in poly.getVarsIndexes():
            return True
        else:
            return False

    for poly in poly_prod.polynomials:
        if poly.degree.a <= -1 and len(poly.monomials) == 1 and not len(poly.getVarsIndexes()) == 0:
            pole_var = list(poly.getVarsIndexes())[0]

            if not stretched(poly_prod, pole_var):
                result_poly = copy.deepcopy(poly_prod)
                coefficient = polynomial.poly([(1, []), ], degree=1, c=poly.c)
                result_poly.polynomials.remove(poly)
                result_poly *= coefficient
                return [result_poly, poly]

    return []


def extract_eps_poles(polypr, toIndex):
    """
    returns dictionary eps degree -> polynomial product list
    every polynomial product list represents a sum
    :param polypr:
    :param toIndex:
    """

    old_expansion = dict()
    new_expansion = dict()
    old_expansion[0] = [polypr, ]
    need_another_go = False

    while True:
        for k in old_expansion.keys():
            need_another_go = False
            old_expansion[k] = map(lambda x: x.simplify(), old_expansion[k])

            for current_poly_prod in old_expansion[k]:
                check_result = remove_pole(current_poly_prod)
                found_pole = (not 0 == len(check_result))

                if found_pole:
                    need_another_go = True
                    P1 = check_result[0]
                    poly = check_result[1]
                    pole_var = list(poly.getVarsIndexes())[0]

                    cont = analytical_continuation(P1, pole_var, poly.degree.a, poly.degree.b, toIndex)
                    for k1 in cont.keys():
                        if k + k1 in new_expansion.keys() and k + k1 <= toIndex:
                            new_expansion[k + k1] += copy.deepcopy(cont[k1])
                        else:
                            new_expansion[k + k1] = copy.deepcopy(cont[k1])
                else:
                    if k not in new_expansion.keys():
                        new_expansion[k] = []
                    new_expansion[k].append(current_poly_prod)
        if not need_another_go:
            new_expansion.clear()
            break
        else:
            old_expansion.clear()
            old_expansion = copy.deepcopy(new_expansion)
            new_expansion.clear()

    for i in range(min(old_expansion.keys()), toIndex + 1):
        new_expansion[i] = []

    refactored_exp = dict()
    for k in sorted(old_expansion.keys()):
        for current_poly_prod in old_expansion[k]:
            exp = current_poly_prod.epsExpansion(toIndex - k)

            for k2 in exp[1].keys():
                exp[1][k2] = filter(lambda a: a.c != 0, exp[1][k2])
                if len(exp[1][k2]) != 0:
                    refactored_exp[k2] = [exp[0], exp[1][k2]]

            for k2 in refactored_exp.keys():
                if k + k2 in new_expansion.keys():
                    new_expansion[k + k2].append(refactored_exp[k2])

            refactored_exp.clear()

    old_expansion.clear()
    old_expansion = copy.deepcopy(new_expansion)
    new_expansion.clear()

    for k in old_expansion.keys():
        if len(old_expansion[k]) == 0:
            old_expansion.pop(k, None)

    return old_expansion