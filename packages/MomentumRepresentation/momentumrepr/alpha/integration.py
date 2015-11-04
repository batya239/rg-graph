#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

OPERATIONS = set()
OPERATIONS.add("log")
OPERATIONS.add("p2")
OPERATIONS.add("iw")

from rggraphenv import symbolic_functions
from rggraphutil import zeroDict

from momentumrepr import configure_mr
from momentumrepr import spherical_coordinats, graph_util_mr
import feyn_representation
import cuba_integration
import time_versions
import sector_decomposition
import polynomial
import swiginac


pi = symbolic_functions.Pi
gamma = symbolic_functions.tgamma


def integrate(graph, operation):
    result = zeroDict()
    tvs = time_versions.find_time_versions(graph)
    print "Time version count:", len(tvs)
    for g in tvs:
        print "Time Version:", g
        for o, v in integrate_time_version(g, operation).iteritems():
            result[o] += v
    return result


def integrands(graph, operation):
    graph = graph_util_mr.from_str_alpha(graph)
    tvs = time_versions.find_time_versions(graph)
    print "Time version count:", len(tvs)
    for g in tvs:
        print "Time Version:", g
        yield integrand_time_version(g, operation)


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


def integrand_time_version(graph, operation):
    c, _d, c_tau, c_d_tau, c_omega, v_substitutor, v_params, v_rate, tau_rate, graph = feyn_representation.get_polynomials(graph, p2=operation == "p2")

    tau_c = polynomial.poly(map(lambda u: (1, (u,)), c_tau))
    omega_c = polynomial.poly(map(lambda u: (1, u), c_omega))



    c_d_tau = tau_multiplier(tau_rate, v_rate)

    __d = _d
    __c = c
    __c_tau = tau_c
    for u, subs in v_substitutor.iteritems():
        __d = __d.changeVarToPolynomial(u, subs)
        __c = __c.changeVarToPolynomial(u, subs)
        __c_tau = __c_tau.changeVarToPolynomial(u, subs)
    __d1 = fix_v(__d.toPolyProd(), v_rate)
    __c1 = fix_v(__c.toPolyProd(), v_rate)
    if configure_mr.Configure.debug():

        print "Substituted D:", __d1
        print "Substituted C:", __c1
        print "Substituted C_tau:", __c_tau
    sectors = sector_decomposition.calculate_sectors(sector_decomposition.strategy_a, __d, graph)
    sectors = sectors.get_all_sectors()
    if configure_mr.Configure.debug():
        for s in sectors:
            print "Sector Substitutor:", s

    l = graph.loops_count
    d = configure_mr.Configure.dimension()

    # sum(alphas) + 1
    alpha = len(graph.vertices) - 1
    if configure_mr.Configure.debug():
        print "Alpha:", alpha

    dl2 = d * l / symbolic_functions.CLN_TWO
    base_c = pi ** dl2 * gamma(alpha - dl2) / (spherical_coordinats.sphere_square(d) ** l)
    base_c = base_c.simplify_indexed()
    for p in v_rate.values():
        base_c /= swiginac.tgamma(symbolic_functions.cln(p))
        # base_c /= swiginac.tgamma(symbolic_functions.cln(p + 1))
    if configure_mr.Configure.debug():
        print "BaseC:", base_c

    dl2_pair = configure_mr.Configure.dimension_pair() * l / 2
    d2_pair = configure_mr.Configure.dimension_pair() / 2

    def tau_omega_multiplier():
        if operation == "iw":
            assert omega_c is not None
            _base_c = - (dl2 - alpha)
            ret = tau_c.changeDegree(dl2_pair - alpha - 1) * omega_c
        else:
            if operation == "p2":
                _base_c = (dl2 - alpha)
                ret = tau_c.changeDegree(dl2_pair - alpha - 1)
            else:
                _base_c = symbolic_functions.CLN_ONE
                ret = tau_c.changeDegree(dl2_pair - alpha)
        if configure_mr.Configure.debug():
            print "Tau-omega multiplier:", ret
            print "Tau-omega base const:", _base_c
        return ret, _base_c

    _d = _d.changeDegree((-d2_pair - 1) if operation == "p2" else (- d2_pair))

    c = c if operation == "p2" else polynomial.poly([(1, tuple())])

    multiplier = tau_omega_multiplier()
    exprs = multiplier[0] * c * _d

    base_c *= multiplier[1]

    def subs_u(expr, c_d_tau):
        for u, p in v_substitutor.iteritems():
            expr = expr.changeVarToPolynomial(u, p)
        expr = fix_v(expr, v_rate)
        raw_multiplier = list()
        for v, p in v_rate.iteritems():
            raw_multiplier += [v] * (p - 1)
        return expr * polynomial.poly([(1, raw_multiplier)]) * c_d_tau
    exprs = subs_u(exprs, c_d_tau)
    exprs = exprs.simplify()
    if configure_mr.Configure.debug():
        print "Expression:", exprs

    sub_graph_infos = feyn_representation.find_sub_graphs_info(graph)[1]
    exprs = [exprs]

    for sg_info in sub_graph_infos:
        a = feyn_representation.AlphaParameter(sg_info.idx, "a")
        assert sg_info.divergence in (0, 2)
        if configure_mr.Configure.debug():
            print "Stretcher: %s, Divergence: %s" % (a, sg_info.divergence)
        canonical_dim = 1 + sg_info.divergence / 2
        if canonical_dim == 1:
            exprs = reduce(lambda l, e: l + e.diff(a, 1), exprs, list())
            pass
        elif canonical_dim == 2:
            exprs = reduce(lambda l, e: l + e.diff(a, 2), exprs, list())
            a_multiplier = polynomial.poly([(1, []), (-1, [a])])
            exprs = map(lambda e: e * a_multiplier, exprs)
            pass
        else:
            raise AssertionError()

    sector_exprs = list()
    conditions = list()
    removed_vars = list()
    delta_arg_base = construct_delta(v_params)
    if configure_mr.Configure.debug():
        print "Base delta:", delta_arg_base


    for subs in sectors:
        if configure_mr.Configure.debug():
            print "Sector:", subs
        es, delta_arg = polynomial.sd_lib.sectorDiagram(exprs, subs, delta_arg_base, False)

        multiplier, theta_arg, additional_v_subs = resolve_delta(delta_arg, subs[0][0])
        conditions.append(theta_arg)
        removed_vars.append(subs[0][0])

        es = map(lambda e: (e * multiplier).simplify().asSwiginac(lambda v: v.as_var()), es)
        es = reduce(lambda a, b: a + b, es, symbolic_functions.CLN_ZERO)

        sector_exprs.append(es)

    all_params = reduce(lambda s, e: s | e.getVarsIndexes(), exprs, set())

    if configure_mr.Configure.debug():
        print "Substitutions:", v_substitutor
        print "Base C:", base_c.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, 3)

    sector_exprs = map(lambda e: eps_expansion(e, configure_mr.Configure.target_loops_count() - graph.loops_count + 1), sector_exprs)

    return base_c.subs(symbolic_functions.e == 0).to_double(), (sector_exprs, all_params, conditions, removed_vars)


def integrate_time_version(graph, operation):
    c, _d, c_tau, c_d_tau, c_omega, v_substitutor, v_params, v_rate, tau_rate, graph = feyn_representation.get_polynomials(graph, p2=operation == "p2")

    tau_c = polynomial.poly(map(lambda u: (1, (u,)), c_tau))
    omega_c = polynomial.poly(map(lambda u: (1, u), c_omega))

    c_d_tau = tau_multiplier(tau_rate)

    __d = _d
    __c = c
    __c_tau = tau_c
    for u, subs in v_substitutor.iteritems():
        __d = __d.changeVarToPolynomial(u, subs)
        __c = __c.changeVarToPolynomial(u, subs)
        __c_tau = __c_tau.changeVarToPolynomial(u, subs)
    __d1 = fix_v(__d.toPolyProd(), v_rate)
    __c1 = fix_v(__c.toPolyProd(), v_rate)
    if configure_mr.Configure.debug():

        print "Substituted D:", __d1
        print "Substituted C:", __c1
        print "Substituted C_tau:", __c_tau
    sectors = sector_decomposition.calculate_sectors(sector_decomposition.strategy_a, __d, graph)
    sectors = sectors.get_all_sectors()
    if configure_mr.Configure.debug():
        for s in sectors:
            print "Sector Substitutor:", s

    l = graph.loops_count
    d = configure_mr.Configure.dimension()

    # sum(alphas) + 1
    alpha = len(graph.vertices) - 1
    if configure_mr.Configure.debug():
        print "Alpha:", alpha

    dl2 = d * l / symbolic_functions.CLN_TWO
    base_c = pi ** dl2 * gamma(alpha - dl2) / (spherical_coordinats.sphere_square(d) ** l)
    base_c = base_c.simplify_indexed()
    for p in v_rate.values():
        base_c /= swiginac.tgamma(symbolic_functions.cln(p))
        # base_c /= swiginac.tgamma(symbolic_functions.cln(p + 1))
    if configure_mr.Configure.debug():
        print "BaseC:", base_c

    dl2_pair = configure_mr.Configure.dimension_pair() * l / 2
    d2_pair = configure_mr.Configure.dimension_pair() / 2

    def tau_omega_multiplier():
        if operation == "iw":
            assert omega_c is not None
            _base_c = - (dl2 - alpha)
            ret = tau_c.changeDegree(dl2_pair - alpha - 1) * omega_c
        else:
            if operation == "p2":
                _base_c = (dl2 - alpha)
                ret = tau_c.changeDegree(dl2_pair - alpha - 1)
            else:
                _base_c = symbolic_functions.CLN_ONE
                ret = tau_c.changeDegree(dl2_pair - alpha)
        if configure_mr.Configure.debug():
            print "Tau-omega multiplier:", ret
            print "Tau-omega base const:", _base_c
        return ret, _base_c

    _d = _d.changeDegree((-d2_pair - 1) if operation == "p2" else (- d2_pair))

    c = c if operation == "p2" else polynomial.poly([(1, tuple())])

    multiplier = tau_omega_multiplier()
    exprs = multiplier[0] * c * _d

    base_c *= multiplier[1]

    def subs_u(expr, c_d_tau):
        for u, p in v_substitutor.iteritems():
            expr = expr.changeVarToPolynomial(u, p)
        expr = fix_v(expr, v_rate)
        raw_multiplier = list()
        for v, p in v_rate.iteritems():
            raw_multiplier += [v] * (p - 1)
        return expr * polynomial.poly([(1, raw_multiplier)]) * c_d_tau
    exprs = subs_u(exprs, c_d_tau)
    exprs = exprs.simplify()
    if configure_mr.Configure.debug():
        print "Expression:", exprs

    sub_graph_infos = feyn_representation.find_sub_graphs_info(graph)[1]
    exprs = [exprs]

    for sg_info in sub_graph_infos:
        a = feyn_representation.AlphaParameter(sg_info.idx, "a")
        assert sg_info.divergence in (0, 2)
        if configure_mr.Configure.debug():
            print "Stretcher: %s, Divergence: %s" % (a, sg_info.divergence)
        canonical_dim = 1 + sg_info.divergence / 2
        if canonical_dim == 1:
            exprs = reduce(lambda l, e: l + e.diff(a, 1), exprs, list())
            pass
        elif canonical_dim == 2:
            exprs = reduce(lambda l, e: l + e.diff(a, 2), exprs, list())
            a_multiplier = polynomial.poly([(1, []), (-1, [a])])
            exprs = map(lambda e: e * a_multiplier, exprs)
            pass
        else:
            raise AssertionError()

    sector_exprs = list()
    conditions = list()
    removed_vars = list()
    delta_arg_base = construct_delta(v_params)
    if configure_mr.Configure.debug():
        print "Base delta:", delta_arg_base


    for subs in sectors:
        if configure_mr.Configure.debug():
            print "Sector:", subs
        es, delta_arg = polynomial.sd_lib.sectorDiagram(exprs, subs, delta_arg_base, False)

        multiplier, theta_arg, additional_v_subs = resolve_delta(delta_arg, subs[0][0])
        conditions.append(theta_arg)
        removed_vars.append(subs[0][0])

        es = map(lambda e: (e * multiplier).simplify().asSwiginac(lambda v: v.as_var()), es)
        es = reduce(lambda a, b: a + b, es, symbolic_functions.CLN_ZERO)

        sector_exprs.append(es)

    all_params = reduce(lambda s, e: s | e.getVarsIndexes(), exprs, set())

    if configure_mr.Configure.debug():
        print "Substitutions:", v_substitutor
        print "Base C:", base_c.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, 3)

    sector_exprs = map(lambda e: eps_expansion(e, configure_mr.Configure.target_loops_count() - graph.loops_count + 1), sector_exprs)

    integration_result = cuba_integration.cuba_integrate(sector_exprs, all_params, conditions, removed_vars)
    return multiply(integration_result, base_c, graph)


def tau_multiplier(tau_rate):
    monomials = dict()
    # alpha_prod = reduce(lambda x, y: x * y, v_rate.values(), 1)

    for v, (c, stretchers) in tau_rate.iteritems():
        # coeff = c * alpha_prod
        # if str(v) == "v0":
        #     continue
        coeff = c
        raw_monomial = {v: 1}
        for stretcher in stretchers:
            raw_monomial[stretcher] = 1
        monomials[polynomial.multiindex.MultiIndex(raw_monomial)] = coeff
    return polynomial.polynomial.Polynomial(monomials)


def eps_expansion(expr, order):
    expr_series = expr.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, order)
    result = dict()
    for i in xrange(order):
        if i == 0:
            result[0] = expr.subs(symbolic_functions.e == symbolic_functions.CLN_ZERO)
        else:
            result[i] = expr_series.coeff(symbolic_functions.e ** symbolic_functions.cln(i))
    return result


def multiply(integration_result, base_c, graph):
    base_c_series = base_c.series(symbolic_functions.e == 0, configure_mr.Configure.target_loops_count() + 1 - graph.loops_count)
    result = zeroDict()
    for eps_order in xrange(configure_mr.Configure.target_loops_count() + 1 - graph.loops_count):
        for j in xrange(eps_order + 1):
            i = eps_order - j
            result[eps_order] += integration_result[i] * (base_c_series.subs(symbolic_functions.e == 0) if j == 0 else base_c_series.coeff(symbolic_functions.e ** j)).simplify_indexed().evalf().to_double()
    return result


def resolve_delta(delta_arg, primary_var):
    delta_arg = delta_arg.toPolyProd().simplify()
    multiplier = polynomial.poly([(1, (primary_var, ))])
    delta_arg = (delta_arg * multiplier.changeDegree(-1)).simplify()
    return multiplier, delta_arg, polynomial.polynomial_product.PolynomialProduct(map(lambda p: p ** (-1), delta_arg.polynomials))


def construct_delta(vs):
    monomials = list()
    for v in vs:
        monomials.append((1, (v,)))
    return polynomial.poly(monomials)


