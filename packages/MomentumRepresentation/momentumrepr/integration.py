#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'


import collections
import spherical_coordinats
import configure
import swiginac
import spherical_coordinats
import time_versions
import scalar_product
from rggraphenv import symbolic_functions


Integration = collections.namedtuple("Integration", ["var", "a", "b"])


def get_base_integrand(graph_with_time_version):
    v = time_versions.substitute(graph_with_time_version)
    v *= scalar_product.substitute_scalar_product(graph_with_time_version.graph)
    return v


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


def construct_integrand(base_integrand, loop_momentum_vars, stretch_vars, angles):
    dimension = configure.Configure.dimension()

    integrand = base_integrand
    integrations = list()

    free_sphere_dimension = dimension
    for angle in angles:
        free_sphere_dimension -= symbolic_functions.CLN_ONE
        integrations.append(Integration(var=angle, a=symbolic_functions.CLN_ZERO, b=symbolic_functions.Pi))

    integrand *= spherical_coordinats.sphere_square(free_sphere_dimension)

    for loop_var in loop_momentum_vars:
        integrand *= loop_var ** (dimension - symbolic_functions.CLN_ONE)
        integrand = integrand.subs(loop_var == (loop_var / (symbolic_functions.CLN_ONE + loop_var)))
        integrations.append(Integration(var=loop_var, a=symbolic_functions.CLN_ZERO, b=symbolic_functions.CLN_ONE))

    for_diff = integrand
    integrand = symbolic_functions.CLN_ONE if len(stretch_vars) else integrand
    for s_v in stretch_vars:
        var = s_v.var
        divergence = s_v.divergence
        integrand *= (symbolic_functions.CLN_ONE / swiginac.factorial(divergence)) * \
                     (symbolic_functions.CLN_ONE - var) ** divergence \
                     * for_diff.diff(var, divergence + 1)
        integrations.append(Integration(var=var, a=symbolic_functions.CLN_ZERO, b=symbolic_functions.CLN_ONE))

    return integrand, integrations


