#!/usr/bin/python
# -*- coding: utf8
import hardcoded
import graphine
import sym_coef
import swiginac
from rggraphenv import symbolic_functions

__author__ = 'dima'


u = symbolic_functions.var("u")

g_2t = dict()
g_2t[1] = filter(lambda x: x.external_edges_count == 2, map(graphine.Graph, hardcoded.ONE_LOOP.keys()))
g_2t[2] = filter(lambda x: x.external_edges_count == 2, map(graphine.Graph, hardcoded.TWO_LOOPS.keys()))

g_3t = dict()
g_3t[1] = filter(lambda x: x.external_edges_count == 3, map(graphine.Graph, hardcoded.ONE_LOOP.keys()))
g_3t[2] = filter(lambda x: x.external_edges_count == 3, map(graphine.Graph, hardcoded.TWO_LOOPS.keys()))

Z = dict()

for op in ("p2", "iw", "tau"):
    z_sum = symbolic_functions.CLN_ZERO
    for loops, graphs in g_2t.items():
        z_sum_c = symbolic_functions.CLN_ZERO
        for g in graphs:
            sc = sym_coef.sc(g)
            z_sum_c += hardcoded.kr1_eps(g, op) * sc * (symbolic_functions.CLN_MINUS_ONE ** (loops + 1))
        z_sum += z_sum_c * u ** loops
    if op == "iw":
        z_sum *= symbolic_functions.CLN_MINUS_ONE
    Z[op] = symbolic_functions.CLN_ONE - z_sum.collect(u)

op = "log"
z_sum = symbolic_functions.CLN_ZERO
for loops, graphs in g_3t.items():
    z_sum_c = symbolic_functions.CLN_ZERO
    for g in graphs:
        sc = sym_coef.sc(g)
        z_sum_c += hardcoded.kr1_eps(g, op) * sc * (symbolic_functions.CLN_MINUS_ONE ** (loops + 2))
    z_sum += z_sum_c * u ** loops
Z[op] = ((symbolic_functions.CLN_ONE - z_sum.collect(u)) ** symbolic_functions.CLN_TWO).series(u == symbolic_functions.CLN_ZERO, 3).collect(u).convert_to_poly(no_order=True)


def gamma(z):
    z = z.collect(symbolic_functions.e)
    coeff_minus_one = z.coeff(symbolic_functions.e ** (-1))
    return - 2 * coeff_minus_one.diff(u, 1) * u


def beta_div_u():
    return (- symbolic_functions.e + gamma(Z["iw"]) + symbolic_functions.CLN_TWO * gamma(Z["p2"]) - gamma(Z["log"])).expand()

for k, v in Z.iteritems():
    v = v.subs(symbolic_functions.e == symbolic_functions.e / symbolic_functions.CLN_TWO)
    print "Z_" + k, v.coeff(u ** 1).simplify_indexed(), v.coeff(u ** 2).simplify_indexed()


u_subs = symbolic_functions.CLN_ZERO
for i in xrange(1, 1 + 2):
    u_subs += symbolic_functions.var("u" + str(i)) * symbolic_functions.e ** i
beta_series = beta_div_u().subs(u == u_subs).collect(symbolic_functions.e).series(symbolic_functions.e == 0, 2 + 1)

found_expansion = dict()
for i in xrange(1, 1 + 2):
    u_current = symbolic_functions.var("u" + str(i))
    coefficient = beta_series.coeff(symbolic_functions.e ** i)
    for k, v in found_expansion.iteritems():
        coefficient = coefficient.subs(k == v)
    found_expansion[u_current] = swiginac.lsolve(coefficient == symbolic_functions.CLN_ZERO, u_current)

print found_expansion