#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import sector_decomposition
import time_versions
import polynomial
import swiginac
import feyn_repr
import cuba_integration
from momentumrepr import configure_mr
from rggraphenv import symbolic_functions
from rggraphutil import zeroDict, emptyListDict


ADDITIONAL_OPERATIONS = {None, "p2", "iw"}


cln_4 = symbolic_functions.cln(4)
pi = symbolic_functions.Pi
gamma = symbolic_functions.tgamma
e = symbolic_functions.e


def g11():
    num = (cln_4 * pi) ** (configure_mr.Configure.dimension() / symbolic_functions.cln(2))
    den = symbolic_functions.tgamma(e + symbolic_functions.CLN_ONE)
    return num / den


def calculate_with_tau(graph, additional_operation, insert_p2_dotes=0):
    res = calculate(graph, additional_operation, insert_p2_dotes=insert_p2_dotes)
    return apply_tau(res, graph)


def apply_tau(res, graph):
    result = symbolic_functions.CLN_ZERO
    max_k = -1
    for k, v in res.iteritems():
        result += (v if isinstance(v, float) else v.n) * symbolic_functions.e ** k
        max_k = max(k, max_k)
    result += symbolic_functions.Order(symbolic_functions.e ** (max_k + 1))
    result += symbolic_functions.Order(symbolic_functions.e ** (configure_mr.Configure.target_loops_count() - graph.loops_count))
    result *= symbolic_functions.var("tau") ** (e * graph.loops_count)
    return result

def calculate(graph, additional_operation, insert_p2_dotes=0):
    assert "p2" not in str(graph), (graph, additional_operation)
    return calculate0(graph, additional_operation, insert_p2_dotes)


def calculate0(graph, additional_operation, insert_p2_dotes=0):
    assert additional_operation in ADDITIONAL_OPERATIONS

    result = zeroDict()
    tvs = time_versions.find_time_versions(graph)
    print "Time version count:", len(tvs)
    for g in tvs:
        for o, v in integrate_time_version(g, additional_operation, insert_p2_dotes).iteritems():
            result[o] += v
    return result


def integrate_time_version(graph, operation, insert_p2_dotes=0):

    c, _d, c_tau, c_omega, v_substitutor, v_params, v_rate, tau_rate, graph = feyn_repr.get_polynomials(graph, p2=operation == "p2")

    omega_c = polynomial.poly(map(lambda u: (1, u), c_omega))

    sectors = get_sectors(v_substitutor, _d, graph)
    if configure_mr.Configure.debug():
        for s in sectors:
            print "Sector Substitutor:", s

    l = graph.loops_count
    d = configure_mr.Configure.dimension()

    # sum(alphas) + 1
    alpha = len(graph.vertices) - 2
    if configure_mr.Configure.debug():
        print "Alpha:", alpha


    dl2_pair = configure_mr.Configure.dimension_pair() * l / 2
    d2_pair = configure_mr.Configure.dimension_pair() / 2
    c_tau = polynomial.poly(map(lambda u: (1, (u,)), c_tau))
    c = c if operation == "p2" else polynomial.poly([(1, tuple())])

    exprs = c * c_tau.changeDegree((dl2_pair - alpha - 1) if operation in ("p2", "iw") else (- alpha + dl2_pair)) * (_d.changeDegree((-d2_pair - 1) if operation == "p2" else (- d2_pair)))
    if operation == "iw":
        exprs *= omega_c
    def subs_u(expr):
        for u, p in v_substitutor.iteritems():
            expr = expr.changeVarToPolynomial(u, p)
        expr = fix_v(expr, v_rate)
        raw_multiplier = list()
        for v, p in v_rate.iteritems():
            raw_multiplier += [v] * (p - 1)
        return expr * polynomial.poly([(1, raw_multiplier)])
    exprs = subs_u(exprs)
    exprs = exprs.simplify()
    if configure_mr.Configure.debug():
        print "Expression:", exprs

    sector_exprs = emptyListDict()
    delta_arg_base = construct_delta(v_params)
    if configure_mr.Configure.debug():
        print "Base delta:", delta_arg_base

    for subs in sectors:
        if configure_mr.Configure.debug():
            print "Sector:", subs
        es, delta_arg = polynomial.sd_lib.sectorDiagram(exprs, subs, delta_arg_base, True)
        assert len(es) == 1
        es = es[0].simplify()
        assert_pole_extracting_ready(es)
        tuple_ = map(lambda u: [1, (u,)], subs[0][1]) + [[1, tuple()]]
        es = es.changeVarToPolynomial(subs[0][0], polynomial.poly(tuple_))
        extracted_poles = polynomial.pole_extractor.extract_poles_and_eps_series(es, configure_mr.Configure.target_loops_count() - graph.loops_count)
        if configure_mr.Configure.debug():
            print "Extracted poles", extracted_poles
        for k, v in extracted_poles.items():
            sector_exprs[k] += v

    base_c = get_free_coefficient(graph)
    for p in v_rate.values():
        base_c /= swiginac.tgamma(symbolic_functions.cln(p))
    if operation in ("p2", "iw"):
        base_c *= (d * l / symbolic_functions.CLN_TWO - alpha)
    if operation == "iw":
        base_c *= symbolic_functions.CLN_MINUS_ONE
    if insert_p2_dotes != 0:
        assert insert_p2_dotes in (1, 2)
        pow = ((configure_mr.Configure.dimension() * graph.loops_count) / symbolic_functions.CLN_TWO - symbolic_functions.CLN_ONE) if operation == "p2" else ((configure_mr.Configure.dimension() * graph.loops_count) / symbolic_functions.CLN_TWO)
        base_c *= pow
        #TODO replace with -1 in kr1
        base_c *= (-1) ** insert_p2_dotes
        # if insert_p2_dotes == 2:
        #     base_c *= 2
        if insert_p2_dotes == 2:
            base_c *= (pow + symbolic_functions.CLN_ONE)
        if configure_mr.Configure.debug():
            print "P2 dotes inserted", insert_p2_dotes
    if configure_mr.Configure.debug():
        print "Base C:", base_c.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, 3)
        print "Base C:", base_c.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, 3).simplify_indexed()
        print "Base C:", base_c.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, 4).evalf()

    res = cuba_integration.cuba_integrate(sector_exprs)
    final_res = multiply(res, base_c, graph)
    return final_res


def multiply(integration_result, base_c, graph):
    base_c_series = base_c.series(symbolic_functions.e == 0, graph.loops_count + 3)
    base_c_series2 = (base_c * symbolic_functions.e).series(symbolic_functions.e == 0, graph.loops_count + 3)
    result = zeroDict()
    for eps_order in xrange(-graph.loops_count, configure_mr.Configure.target_loops_count() - graph.loops_count):
        for j in xrange(-1, eps_order + graph.loops_count + 1):
            i = eps_order - j
            result[eps_order] += integration_result[i] * (base_c_series2.coeff(e) if j == 0 else base_c_series.coeff(symbolic_functions.e ** j)).simplify_indexed().evalf().to_double()
    return result


def assert_pole_extracting_ready(expression):
    for p in expression.polynomials:
        if len(p.monomials) > 1:
            unit_found = False
            for k in p.monomials.keys():
                if len(k.vars) == 0:
                    unit_found = True
                    break
            assert unit_found, p


def get_sectors(v_substitutor, _d, graph):
    for u, subs in v_substitutor.iteritems():
        _d = _d.changeVarToPolynomial(u, subs)
    sectors = sector_decomposition.calculate_sectors(sector_decomposition.strategy_a, _d, graph)
    return sectors.get_all_sectors()


def construct_delta(vs):
    monomials = list()
    for v in vs:
        monomials.append((1, (v,)))
    return polynomial.poly(monomials)


def get_free_coefficient(graph):
    d = configure_mr.Configure.dimension()
    l = graph.loops_count
    alpha = len(graph.vertices) - 2
    dl2 = d * l / symbolic_functions.CLN_TWO
    base_c = (cln_4 * pi) ** (-dl2) * gamma(alpha - dl2) * g11() ** graph.loops_count
    base_c = base_c.simplify_indexed()
    return base_c


def fix_v(exprs, v_rate):
    assert isinstance(exprs, polynomial.polynomial_product.PolynomialProduct), type(exprs)
    def fix_polynomial(poly):
        new_monomials = dict()
        for m, c in poly.monomials.iteritems():
            for v, p in m.vars.iteritems():
                if v in v_rate:
                    c_fix = v_rate[v] ** p
                    assert (c / c_fix) * c_fix == c
                    c /= c_fix
            new_monomials[m] = c
        return polynomial.polynomial.Polynomial(new_monomials, degree=poly.degree, c=poly.c, doPrepare=False)
    return polynomial.polynomial_product.PolynomialProduct(map(fix_polynomial, exprs.polynomials))


def resolve_delta(delta_arg, primary_var):
    delta_arg = delta_arg.toPolyProd().simplify()
    multiplier = polynomial.poly([(1, (primary_var, ))])
    delta_arg_tr = (delta_arg * multiplier.changeDegree(-1)).simplify()
    return multiplier, delta_arg_tr, polynomial.polynomial_product.PolynomialProduct(map(lambda p: p ** (-1), delta_arg_tr.polynomials))


def K(a_dict):
    new_dict = dict()
    for k, v in a_dict.iteritems():
        if k < 0:
            new_dict[k] = v
    return new_dict