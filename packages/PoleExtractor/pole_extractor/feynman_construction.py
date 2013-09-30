__author__ = 'gleb'

import copy
import itertools
import polynomial
import math
from . import adjacency_combinatorics as ac


def unique(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]


def determinant(g_info):
    """
    """
    edges = g_info['edges']
    c_laws = g_info['conservation laws']
    loops = g_info['loops']

    det_base = filter(lambda x: g_info['external vertex'] not in g_info['adjacency list'][x][0:2],
                      list(xrange(0, edges)))
    det = unique(map(lambda x: sorted(x), list(itertools.permutations(det_base, loops))))

    for law in filter(lambda x: len(x) == 2, c_laws):
        for monomial in det:
            if law[0] in monomial:
                monomial.remove(law[0])
                monomial.append(law[1])

    det = filter(lambda x: len(x) >= loops, map(lambda y: unique(sorted(y)), det))
    det = filter(lambda x: all(map(lambda y: not set(y).issubset(x), c_laws)), unique(det))

    return det


def numerator(g_info):
    """
    """
    edges = g_info['edges']
    c_laws = g_info['conservation laws']
    num_base = list(xrange(0, edges))

    for law in c_laws:
        if len(law) == 2:
            while law[0] in num_base:
                num_base.remove(law[0])
                num_base.append(law[1])

    for edge in list(xrange(0, edges)):
        if edge in num_base:
            num_base.remove(edge)

    return num_base


def feynman_representation(g_info, PHI_EXPONENT, momentum_derivative=False):
    """
    Output: dictionary with string keys:
    'integrand' -> initial polynomial product representing this diagram,
    'd-func argument' -> argument of delta-function in initial Feynman representation
    'variable list' -> list of variables used in integrand
    'gamma arguments' -> arguments of gamma functions product
    """
    loops = g_info['loops']
    det_base = determinant(g_info)
    num_base = numerator(g_info)

    d_det = map(lambda x: (1, x), det_base)
    d_num = [(1, num_base), ]

    d_arg_set = set([])
    for monomial in det_base:
        for u in monomial:
            d_arg_set.add(u)

    d_arg = map(lambda x: (1, [x, ]), list(d_arg_set))

    if PHI_EXPONENT == 3:
        deg = 3
    elif PHI_EXPONENT == 4:
        deg = 2
    else:
        return 0

    Denominator = polynomial.poly(d_det, degree=(-deg, 1))
    Numerator = polynomial.poly(d_num)
    Delta_argument = polynomial.poly(d_arg)

    Integrand = Denominator * Numerator

    if momentum_derivative:
        new_edge = []
        for edge in g_info['adjacency list']:
            if g_info['external vertex'] in edge[0:2]:
                new_edge += edge[0:2]
        new_edge = filter(lambda x: x != g_info['external vertex'], new_edge)
        diag_for_c = copy.deepcopy(g_info['adjacency list'])
        diag_for_c.append(new_edge)
        diag_for_c_info = ac.graph_info(diag_for_c)

        c_base = determinant(diag_for_c_info)
        d_c = map(lambda x: (1, x), c_base)
        deg_a = -g_info['edges'] + 2 + loops * deg
        deg_b = -loops
        C = polynomial.poly(d_c, degree=(deg_a, deg_b))
        C = C.set0toVar(len(diag_for_c) - 1)
        Integrand = Integrand * C.toPolyProd()

    variables = set([])
    for monomial in det_base:
        for edge in monomial:
            variables.add(edge)

    gamma_arguments = [int] * 4
    gamma_arguments[0] = g_info['edges'] - g_info['tails'] - deg * g_info['loops']
    gamma_arguments[1] = g_info['loops']
    gamma_arguments[2] = deg
    gamma_arguments[3] = -1

    g = dict((i, num_base.count(i)) for i in num_base).values()
    gc = 1
    for i in g:
        gc *= math.factorial(i)
    gc *= 2 ** g_info['loops']
    Integrand.polynomials[0].c *= gc ** (-1)

    f_repr = dict()
    f_repr['integrand'] = Integrand
    f_repr['d-func argument'] = Delta_argument
    f_repr['variable list'] = list(variables)
    f_repr['gamma arguments'] = gamma_arguments

    return f_repr