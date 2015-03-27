#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

OPERATIONS = set()
OPERATIONS.add("log")
OPERATIONS.add("p2")
OPERATIONS.add("iw")

from rggraphenv import symbolic_functions
from rggraphutil import zeroDict

import configure_mr
import spherical_coordinats
import feyn_representation
import cuba_integration
import time_versions
import sector_decomposition
import polynomial


pi = symbolic_functions.Pi
gamma = symbolic_functions.tgamma


def integrate(graph, operation):
    result = zeroDict()
    for g in time_versions.find_time_versions(graph):
        for o, v in integrate_time_version(g, operation).iteritems():
            result[o] += v
    return result


def integrate_time_version(graph, operation):
    c, _d, c_tau, c_omega, v_substitutor, v_params, v_rate, graph = feyn_representation.get_polynomials(graph)

    __d = _d
    for u, subs in v_substitutor.iteritems():
        __d = __d.changeVarToPolynomial(u, subs)
    if configure_mr.Configure.debug():
        print "Substituted D:", __d
    sectors = sector_decomposition.calculate_sectors(sector_decomposition.strategy_a, __d, graph)
    sectors = sectors.get_all_sectors()
    if configure_mr.Configure.debug():
        for s in sectors:
            print "Sector Substitutor:", s

    tau_c = polynomial.poly(map(lambda u: (1, (u,)), c_tau))
    omega_c = polynomial.poly(map(lambda u: (1, (u,)), c_omega))

    l = graph.loops_count
    d = configure_mr.Configure.dimension()
    alpha = len(graph.vertices) - 2
    if configure_mr.Configure.debug():
        print "Alpha:", alpha

    dl2 = d * l / symbolic_functions.CLN_TWO
    base_c = pi ** dl2 * gamma(alpha - dl2) / (spherical_coordinats.sphere_square(d) ** l)
    base_c = base_c.simplify_indexed()
    if configure_mr.Configure.debug():
        print "BaseC:", base_c

    dl2_pair = configure_mr.Configure.dimension_pair() * l / 2.
    d2_pair = configure_mr.Configure.dimension_pair() / 2.

    def tau_omega_multiplier():
        if operation == "iw":
            assert omega_c is not None
            _base_c = - (dl2 - alpha) * (dl2 - alpha - symbolic_functions.CLN_ONE)
            ret = tau_c.changeDegree(dl2_pair - alpha - 1) * omega_c
        else:
            _base_c = (dl2 - alpha)
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

    def subs_u(expr):
        for u, p in v_substitutor.iteritems():
            expr = expr.changeVarToPolynomial(u, p)
        raw_multiplier = list()
        for v, p in v_rate.iteritems():
            raw_multiplier += [v] * (p - 1)
        return expr * polynomial.poly([(1, raw_multiplier)])
    exprs = subs_u(exprs)
    exprs = exprs.simplify()
    if configure_mr.Configure.debug():
        print "Expression:", exprs

    sub_graph_infos = feyn_representation.find_sub_graphs_info(graph)[1]
    exprs = [exprs]

    sector_exprs = list()
    conditions = list()
    removed_vars = list()
    delta_arg_base = construct_delta(v_params)
    if configure_mr.Configure.debug():
        print "Base delta:", delta_arg_base
    for subs in sectors:
        es, delta_arg = polynomial.sd_lib.sectorDiagram(exprs, subs, delta_arg_base, False)
        multiplier, theta_arg, additional_v_subs = resolve_delta(delta_arg, subs[0][0])
        conditions.append(theta_arg)
        removed_vars.append(subs[0][0])
        es = map(lambda e: (e * multiplier).simplify().asSwiginac(lambda v: v.as_var()), es)
        es = reduce(lambda a, b: a + b, es, symbolic_functions.CLN_ZERO)
        if configure_mr.Configure.debug():
            print "Delta multiplier:", multiplier
        for sg_info in sub_graph_infos:
            a = feyn_representation.AlphaParameter(sg_info.idx, "a")
            assert sg_info.divergence in (0, 2)
            if configure_mr.Configure.debug():
                print "Stretcher: %s, Divergence: %s" % (a, sg_info.divergence)
            dv_da = additional_v_subs.asSwiginac(lambda v: v.as_var()).diff(a.as_var())
            for _ in xrange(1 + sg_info.divergence / 2):
                es = diff_a(es, a.as_var(), list(multiplier.getVarsIndexes())[0].as_var(), dv_da)
            if sg_info.divergence == 2:
                a_multiplier = (symbolic_functions.CLN_ONE + a.as_var())
                es *= a_multiplier
        sector_exprs.append(es.normal())

    all_params = reduce(lambda s, e: s | e.getVarsIndexes(), exprs, set())

    if configure_mr.Configure.debug():
        print "Expression:", sector_exprs
        print "Substitutions:", v_substitutor

    sector_exprs = map(lambda e: eps_expansion(e, configure_mr.Configure.target_loops_count() - graph.loops_count + 1), sector_exprs)

    integration_result = cuba_integration.cuba_integrate(sector_exprs, all_params, conditions, removed_vars)
    return multiply(integration_result, base_c, graph)


def eps_expansion(expr, order):
    expr_series = expr.series(symbolic_functions.e == symbolic_functions.CLN_ZERO, order)
    result = dict()
    for i in xrange(order):
        if i == 0:
            result[0] = expr.subs(symbolic_functions.e == symbolic_functions.CLN_ZERO).normal()
        else:
            result[i] = expr_series.coeff(symbolic_functions.e ** symbolic_functions.cln(i)).normal()
    return result


def diff_a(exprs, a_var, reduced_var, reduced_var_jacobian):
    new_exprs = symbolic_functions.CLN_ZERO
    new_exprs += exprs.diff(a_var)
    if str(reduced_var_jacobian) != "0":
        new_exprs += reduced_var_jacobian * exprs.diff(reduced_var)
    return new_exprs.normal()


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


