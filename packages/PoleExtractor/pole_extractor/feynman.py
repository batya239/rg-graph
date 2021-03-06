__author__ = 'gleb'

import itertools
import math
import copy

import polynomial
from polynomial import sd_lib
from polynomial import polynomial_product
import graph_state
import graphine

import reduced_vl


class FeynmanIntegrand:
    def __init__(self, integrand, delta_argument):
        self._integrand = integrand
        self._delta_argument = delta_argument

    def __str__(self):
        if self._delta_argument:
            result = '*DELTA[1-' + str(self._delta_argument) + ']'
        else:
            result = ''
        return str(self._integrand) + result

    def __repr__(self):
        return str(self)

    @staticmethod
    def determinant(variables, loops, conservation_laws):
        det = list(set(map(lambda x: tuple(sorted(x)), list(itertools.permutations(variables, loops)))))
        det = filter(lambda x: all(map(lambda y: not set(y).issubset(x), conservation_laws)), det)
        return map(lambda x: (1, list(x)), det)

    @staticmethod
    def fromRVL(rvl, theory):
        """
        Calculates integrand of Feynman's interpretation if rvl is on zero momenta,
        and d/dp^2 of integrand if rvl is not.
        """
        if not isinstance(rvl, reduced_vl.ReducedVacuumLoop):
            raise TypeError(':param rvl: should be ReducedVacuumLoop, not ' + str(type(rvl)))
        if theory not in (3, 4):
            raise ValueError(':param theory: should equal 3 or 4 for phi^3 and phi^4 accordingly, not ' + str(theory))

        deg = 0 - int(not rvl.zero_momenta())
        if 3 == theory:
            deg -= 3
        elif 4 == theory:
            deg -= 2

        loops = rvl.loops()
        edges = rvl.edges()
        cons_laws = rvl.conservation_laws(exclude_ext_edges=True)

        coef = reduce(lambda x, y: x * y, map(lambda z: math.factorial(z - 1), rvl.edges_weights()))
        integrand = polynomial.poly([(1, sum(map(lambda x: [x[0]] * (x[1] - 1), rvl.edges_with_weights()), []))],
                                    c=(coef**(-1) * 2**(-loops)))

        integrand *= polynomial.poly(FeynmanIntegrand.determinant(edges, loops, cons_laws), degree=(deg, 1))
        d_arg = polynomial.poly(map(lambda x: (1, [x]), edges))

        if not rvl.zero_momenta():
            laws_for_c = rvl.internal_conservation_laws()
            integrand *= polynomial.poly(FeynmanIntegrand.determinant(edges, loops + 1, laws_for_c))

        return FeynmanIntegrand(integrand, d_arg)

    @staticmethod
    def fromRVL_w_symmetries(rvl, theory):
        """
        Calculates integrand of Feynman's interpretation if rvl is on zero momenta,
        and d/dp^2 of integrand if rvl is not.
        """
        def note_c_monomial(graph, monomial):
            g = copy.copy(graph)
            new_edges = []
            for i, edge in enumerate(g.allEdges(nickel_ordering=True)):
                if i in monomial:
                    new_v = g.createVertexIndex()
                    new_edges.append(graph_state.Edge(nodes=(edge.nodes[0], new_v)))
                    new_edges.append(graph_state.Edge(nodes=(edge.nodes[1], new_v)))
                else:
                    new_edges.append(edge)
            return graphine.Graph(new_edges)

        if not isinstance(rvl, reduced_vl.ReducedVacuumLoop):
            raise TypeError(':param rvl: should be ReducedVacuumLoop, not ' + str(type(rvl)))
        if theory not in (3, 4):
            raise ValueError(':param theory: should equal 3 or 4 for phi^3 and phi^4 accordingly, not ' + str(theory))
        if rvl.zero_momenta():
            raise ValueError(':param rvl: rvl.zero_momenta() should be False, this func is for p^2-parts only')

        deg = 0 - int(not rvl.zero_momenta())
        if 3 == theory:
            deg -= 3
        elif 4 == theory:
            deg -= 2

        loops = rvl.loops()
        edges = rvl.edges()
        laws_for_c = rvl.internal_conservation_laws()

        c_base = FeynmanIntegrand.determinant(edges, loops + 1, laws_for_c)

        noted_graphs = map(lambda x: note_c_monomial(rvl.graph(), x[1]), c_base)
        labels = map(lambda x: str(x), noted_graphs)

        new_graphs = []
        seen = set([])
        for graph in noted_graphs:
            if not str(graph) in seen:
                seen.add(str(graph))
                new_graphs.append((labels.count(str(graph)), graph))

        coef = reduce(lambda x, y: x * y, map(lambda z: math.factorial(z - 1), rvl.edges_weights()))
        result = []
        for sym_c, graph in new_graphs:
            vl = reduced_vl.ReducedVacuumLoop.fromGraphineGraph(graph, zero_momenta=False)
            loops = vl.loops()
            edges = vl.edges()
            cons_laws = vl.conservation_laws(exclude_ext_edges=True)

            integrand = polynomial.poly([(1, sum(map(lambda x: [x[0]] * (x[1] - 1), vl.edges_with_weights()), []))],
                                        c=(sym_c * coef**(-1) * 2**(-loops)))

            integrand *= polynomial.poly(FeynmanIntegrand.determinant(edges, loops, cons_laws), degree=(deg, 1))
            d_arg = polynomial.poly(map(lambda x: (1, [x]), edges))

            result.append((copy.copy(vl), FeynmanIntegrand(copy.copy(integrand), copy.copy(d_arg))))

        return result

    def sector_decomposition(self, sector):
        result = copy.deepcopy(self)
        res = sd_lib.sectorDiagram(result._integrand, sector[1], result._delta_argument)[0][0]
        coefficient = polynomial.poly([(1, []), ], degree=1, c=sector[0])
        res *= coefficient.toPolyProd()
        result._delta_argument = None
        result._integrand = res.simplify()
        return result


def ac_principal_part(polyprod, pole_var, pole_degree_a, pole_degree_b):
    """
    part of analytical continuation function. returns 1st of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests
    result = dict()
    poly_list = [polyprod, ]

    for _ in itertools.repeat(None, -pole_degree_a - 1):
        poly_list = sum(map(lambda x: x.diff(pole_var), poly_list), [])

    coef_as_poly = polynomial.poly([(1, []), ],
                                   degree=1, c=(math.factorial(-1 - pole_degree_a) ** (-1)) * (pole_degree_b ** (-1)))
    poly_list = map(lambda x: x.set0toVar(pole_var) * coef_as_poly, poly_list)

    result[-1] = poly_list
    return result


def ac_expansion_part(polyprod, pole_var, pole_degree_a, pole_degree_b, toIndex):
    """
    part of analytical continuation function. returns 2nd of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests
    result = dict()

    if pole_degree_a > -2:
        result[0] = []
        return result

    for k in range(0, toIndex + 1):
        poly_list = [polyprod, ]
        c1 = ((-pole_degree_b) ** k)
        result[k] = []

        for i in range(-pole_degree_a - 1):
            c2 = (math.factorial(i) * (i + pole_degree_a + 1) ** (k + 1)) ** (-1)
            coef_as_poly = polynomial.poly([(1, []), ], degree=1, c=c1 * c2)
            result[k].extend(map(lambda x: x.set0toVar(pole_var) * coef_as_poly, poly_list))
            poly_list = sum(map(lambda x: x.diff(pole_var), poly_list), [])

    return result


def ac_stretched_part(polyprod, pole_var, pole_degree_a, pole_degree_b):
    """
    part of analytical continuation function. returns 3rd of 3 parts of resulting eps expansion.
    """
    #TODO: tests tests tests

    result = dict()
    stretcher = 'a' + str(pole_var)
    poly_list = [polyprod.stretch(stretcher, [pole_var, ]), ]

    for _ in itertools.repeat(None, -pole_degree_a):
        poly_list = sum(map(lambda x: x.diff(stretcher), poly_list), [])

    if pole_degree_a <= -2:
        stretch_factor = polynomial.poly([(1, []), (-1, [stretcher, ])],
                                         degree=(-pole_degree_a - 1, 0), c=(math.factorial(-pole_degree_a - 1) ** (-1)))
        poly_list = map(lambda x: x * stretch_factor, poly_list)

    p = polynomial.poly([(1, [pole_var, ]), ], degree=(pole_degree_a, pole_degree_b))
    poly_list = map(lambda x: x * p.toPolyProd(), poly_list)

    result[0] = poly_list
    return result


def analytical_continuation(polyprod, pole_var, pole_degree_a, pole_degree_b, toIndex):
    """

    """
    res1 = ac_principal_part(polyprod, pole_var, pole_degree_a, pole_degree_b)
    res2 = ac_expansion_part(polyprod, pole_var, pole_degree_a, pole_degree_b, toIndex)
    res3 = ac_stretched_part(polyprod, pole_var, pole_degree_a, pole_degree_b)

    all_keys = set(res1.keys() + res2.keys() + res3.keys())

    result = dict()
    for k in list(all_keys):
        result[k] = []
        if k in res1.keys():
            result[k] += filter(lambda y: not y.isZero(), map(lambda x: x.simplify(), res1[k]))
        if k in res2.keys():
            result[k] += filter(lambda y: not y.isZero(), map(lambda x: x.simplify(), res2[k]))
        if k in res3.keys():
            result[k] += filter(lambda y: not y.isZero(), map(lambda x: x.simplify(), res3[k]))
    return result


def separate_pole(poly_prod):
    """
    Removes a factorised pole from poly_prod if there is one and returns pole and poly_prod without it separately.
    """
    #TODO: tests tests tests
    def stretched(poly, var_index):
        """
        Checks if variable is stretched (if it is we consider pole integrable).
        """
        str_name = 'a' + str(var_index)
        if str_name in poly.getVarsIndexes():
            return True
        else:
            return False

    def is_pole(poly):
        """
        Checks if poly (which should be polynomial.Polynomial) is a pole.
        """
        if poly.degree.a <= -1 and len(poly.monomials) == 1 and not len(poly.getVarsIndexes()) == 0:
            if not stretched(poly_prod, list(poly.getVarsIndexes())[0]):
                return True
        return False

    for poly in poly_prod.polynomials:
        if is_pole(poly):
            coefficient = polynomial.poly([(1, []), ], degree=1, c=poly.c)
            result_poly = polynomial_product.PolynomialProduct(filter(lambda x: not x == poly, poly_prod.polynomials))
            if result_poly.isZero():
                result_poly = coefficient
            else:
                result_poly *= coefficient
            return result_poly, poly

    return tuple()


def extract_poles(polypr, toIndex):
    """
    :param polypr:
    :param toIndex:
    :return:
    """
    def extraction_step(expansion):
        result = dict()
        for k in expansion.keys():
            for p_prod in expansion[k]:
                pole_separated = separate_pole(p_prod)
                if not 0 == len(pole_separated):
                    a_part = pole_separated[0]
                    p_part = pole_separated[1]
                    pole_var = list(p_part.getVarsIndexes())[0]

                    cont = analytical_continuation(a_part, pole_var, p_part.degree.a, p_part.degree.b, toIndex)

                    for k1 in cont.keys():
                        if k + k1 <= toIndex:
                            if k + k1 not in result.keys():
                                result[k + k1] = []
                            result[k + k1] += cont[k1]
                else:
                    if k not in result.keys():
                        result[k] = []
                    result[k].append(p_prod)
        return result

    expansion = dict()
    expansion[0] = [polypr, ]
    l = 0

    while l < sum(map(lambda x: len(x), expansion.values())):
        l = sum(map(lambda x: len(x), expansion.values()))
        expansion = extraction_step(expansion)

    result = dict((k, []) for k in list(set(expansion.keys() + range(toIndex + 1))))
    for k in expansion.keys():
        for polypr in expansion[k]:
            exp = polypr.epsExpansion(toIndex - k)
            for k2 in exp[1].keys():
                exp[1][k2] = filter(lambda a: not a.isZero(), exp[1][k2])
                if len(exp[1][k2]) != 0 and k + k2 in result.keys():
                    result[k + k2].append([exp[0], exp[1][k2]])

    return result