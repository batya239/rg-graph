#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import collections
import spherical_coordinats
import configure_mr
import swiginac
import spherical_coordinats
import time_versions
import scalar_product
import swiginac
from rggraphenv import symbolic_functions
from rggraphutil import Ref


Integration = collections.namedtuple("Integration", ["var", "a", "b"])
ScalarProductFunction = collections.namedtuple("ScalarProductFunction", ["sign", "body"])



def get_base_integrand_and_angles(graph_with_time_version):
    v, scalar_products = time_versions.substitute(graph_with_time_version)
    v *= scalar_product.substitute_scalar_product(graph_with_time_version.graph)
    return v, scalar_products


def get_loop_momentum_vars(graph_with_time_version):
    graph = graph_with_time_version.graph
    loop_momentums_vars = set()
    for e in graph.allEdges():
        loop_momentums_vars |= e.flow.get_loop_momentas()
    return loop_momentums_vars


def get_stretch_vars(graph_with_time_version):
    graph = graph_with_time_version.graph
    stretch_vars = set()
    for e in graph.allEdges():
        stretch_vars |= e.flow.get_stretch_vars()
    return stretch_vars


def get_angles(graph_with_time_version):
    graph = graph_with_time_version.graph
    sp = scalar_product.extract_scalar_products(graph)
    if sp is None:
        return tuple()
    substitutor, dimensioned_omegas = spherical_coordinats.ScalarProductEnumerator.enumerate(sp, graph.getLoopsCount())
    variables = set()
    for s in substitutor.values():
        variables |= set(s.variables)
    return variables


def construct_integrand(base_integrand, loop_momentum_vars, stretch_vars, angles, coeff):
    dimension = configure_mr.Configure.dimension()

    if configure_mr.Configure.debug():
        print "Integrand: %s\nLoop momentums: %s\nStretch vars: %s\nAngles: %s" % (base_integrand, loop_momentum_vars, stretch_vars, angles)

    integrand_e = coeff
    integrand_a = base_integrand

    integrations = list()

    free_sphere_dimension = dimension
    scalar_products_functions = list()
    angle_integrations = set()

    for angle in angles:
        free_sphere_dimension -= symbolic_functions.CLN_ONE
        expression = angle.expression
        for v in angle.variables:
            expression = expression.subs(v == swiginac.Pi * v)
            angle_integrations.add(Integration(var=v, a=symbolic_functions.CLN_ZERO, b=symbolic_functions.CLN_ONE))
        scalar_products_functions.append(ScalarProductFunction(angle.fake_variable, expression))
    integrations += list(angle_integrations)

    for angle_integration in angle_integrations:
        integrand_e *= (swiginac.sin(angle_integration.var)) ** (dimension - 2)
        integrand_e *= swiginac.Pi
        integrand_e = integrand_e.subs(angle_integration.var == (angle_integration.var * swiginac.Pi))
        integrand_e *= spherical_coordinats.sphere_square(dimension - 1) / spherical_coordinats.sphere_square(dimension)
        if configure_mr.Configure.debug():
            print "Angle integration:", swiginac.Pi * (swiginac.sin(swiginac.Pi * angle_integration.var)) ** (dimension - 2) * spherical_coordinats.sphere_square(dimension - 1) / spherical_coordinats.sphere_square(dimension)

    for loop_var in loop_momentum_vars:
        integrand_e *= loop_var ** (dimension - symbolic_functions.CLN_ONE)
        integrand_a = integrand_a.subs(loop_var == ((symbolic_functions.CLN_ONE - loop_var) / loop_var))
        integrand_e = integrand_e.subs(loop_var == ((symbolic_functions.CLN_ONE - loop_var) / loop_var))
        integrand_a *= loop_var ** (-2)
        integrations.append(Integration(var=loop_var, a=symbolic_functions.CLN_ZERO, b=symbolic_functions.CLN_ONE))


    integrand_a = integrand_a.normal()
    if configure_mr.Configure.debug():
        print "Integrand(a):", integrand_a
    for s_v in stretch_vars:
        var = s_v.var
        divergence = s_v.divergence
        integrand_a = (symbolic_functions.CLN_ONE / swiginac.factorial(divergence)) * \
                     (symbolic_functions.CLN_ONE - var) ** divergence \
                     * integrand_a.diff(var, divergence + 1).normal()
        integrations.append(Integration(var=var, a=symbolic_functions.CLN_ZERO, b=symbolic_functions.CLN_ONE))

    if configure_mr.Configure.debug():
        print "Integrand(e):", integrand_e
        print "D(a)Integrand(a):", integrand_a

    integrand_series = integrand_e.series(symbolic_functions.e == 0,
                                          configure_mr.Configure.target_loops_count() + 1 - len(loop_momentum_vars)).normal()
    integrand_series_map = dict()
    for degree in xrange(integrand_series.ldegree(symbolic_functions.e), integrand_series.degree(symbolic_functions.e)):
        if degree == 0:
            if configure_mr.Configure.debug():
                print "Eps=0", integrand_e.subs(symbolic_functions.e == 0).normal()
            integrand_series_map[degree] = integrand_e.subs(symbolic_functions.e == 0).normal() * integrand_a
        else:
            integrand_series_map[degree] = integrand_series.coeff(symbolic_functions.e ** degree).normal() * integrand_a
        if configure_mr.Configure.debug():
            print "Integrand by series: %s = %s" % (degree, integrand_series_map[degree])
    if configure_mr.Configure.debug():
        print "ID: %s" % id(integrand_series_map)
    return integrand_series_map, integrations, scalar_products_functions