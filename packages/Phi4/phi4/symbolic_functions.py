#!/usr/bin/python
# -*- coding: utf8
#
#
# definitions of g-functions
#
import re
import rggraphenv
import swiginac

p, e = rggraphenv.cas_variable_resolver.var("p e")
l = 1 - e


zero = swiginac.numeric(0)
tgamma = swiginac.tgamma
Pi = swiginac.Pi
psi = swiginac.psi
zeta = swiginac.zeta
Euler = swiginac.Euler
log = swiginac.log

D = 4 - 2 * e

p2 = p ** 2

pe = p ** e


def series(expression, x, x0, n, remove_order=False):
    res = expression.series(x == x0, n)
    return res.convert_to_poly(no_order=True) if remove_order else res


def subs(expression, z, z0):
    return expression.subs(z == z0)


# noinspection PyUnusedLocal
def evaluate_series(expression_as_string, line_tuple, only_pole_part=False):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-l*2)*G(1, 4-l*3)'
    lineTuple like (4, -4) ~ 4 - 4 * l
    """
    #expansion
    _series = evaluate(expression_as_string, line_tuple).series(e == 0, 0)
    return _series.convert_to_poly(True) if only_pole_part else _series


# noinspection PyUnusedLocal
def evaluate(expression_as_str, line_tuple=None):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-l*2)*G(1, 4-l*3)'
    lineTuple like (4, -4) ~ 4 - 4 * l
    """
    eps_part = eval(to_internal_code(expression_as_str))
    if not line_tuple:
        return eps_part
    line_part = p ** ((-2) * (line_tuple[0] + line_tuple[1] * l))
    return eps_part * line_part


def safe_integer_numerators(expression_as_str):
    #return re.sub('([\.\d]+)/', 'swiginac.numeric(\\1)/', expression_as_str)
    return re.sub('([\.\d]+)/', '\\1./', expression_as_str)


def to_internal_code(expression_as_str):
    return safe_integer_numerators(expression_as_str)


def pole_part(expr):
    return expr.series(e == 0, 0).convert_to_poly(True)


def G(alpha, beta):
    if alpha == 1 and beta == 1:
        return 1 / e
    return _raw_g(alpha, beta) / _g11


def G1(alpha, beta):
    return (G(alpha, beta) + G(alpha - 1, beta) - G(alpha, beta - 1))/2


def G2(alpha, beta):
    return (G(alpha, beta) - G(alpha - 1, beta) - G(alpha, beta - 1))/2


def _raw_g(alpha, beta):
    #noinspection PyUnresolvedReferences
    if (alpha + zero).is_equal(zero) or (beta + zero).is_equal(zero) \
        or (2 * l + 2 - alpha - beta + zero).is_equal(zero):
        return 0
    return tgamma(l + 1 - alpha) * tgamma(l + 1 - beta) * tgamma(alpha + beta - l - 1) \
           / ((4 * Pi) ** (l + 1) * tgamma(alpha) * tgamma(beta) * tgamma(2 * l + 2 - alpha - beta))


_g11 = _raw_g(1, 1) * e