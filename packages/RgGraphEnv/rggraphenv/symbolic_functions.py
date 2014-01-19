#!/usr/bin/python
# -*- coding: utf8
#
#
# definitions of g-functions
#
import re
import swiginac


_vars = dict()


def var(names):
    """
    sympy style "a b c"
    """
    n_vars = []
    names_split = names.split()
    for n in names_split:
        assert len(n) != 0
        v = _vars.get(n, None)
        if v is None:
            v = swiginac.symbol(n)
            _vars[n] = v
        n_vars.append(v)
    return n_vars if len(n_vars) > 1 else n_vars[0]

p, e = var("p e")
l = 1 - e
Z_5_3 = var("Z_5_3")

exp = swiginac.exp
zero = swiginac.numeric(0)
tgamma = swiginac.tgamma
Pi = swiginac.Pi
psi = swiginac.psi
zeta = swiginac.zeta
Euler = swiginac.Euler
log = swiginac.log
Order = swiginac.Order
O = Order

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
    return re.sub('([\.\d]+)/', 'swiginac.numeric(\'\\1\')/', expression_as_str)
    #return re.sub('([\.\d]+)/', '\\1./', expression_as_str)


def to_internal_code(expression_as_str):
    return safe_integer_numerators(expression_as_str)


def pole_part(expr):
    return expr.series(e == 0, 0).convert_to_poly(no_order=True)


#noinspection PyPep8Naming
def G(alpha, beta, d=D):
    if alpha == 1 and beta == 1:
        return 1 / e
    return _raw_g(alpha, beta, d=d) / _g11(d=d)


#noinspection PyPep8Naming
def G1(alpha, beta, d=D):
    return (G(alpha, beta, d=d) + G(alpha - 1, beta, d=d) - G(alpha, beta - 1, d=d))/2


#noinspection PyPep8Naming
def G2(alpha, beta, d=D):
    return (G(alpha, beta, d=d) - G(alpha - 1, beta, d=d) - G(alpha, beta - 1, d=d))/2


def _raw_g(alpha, beta, d=D):
    #noinspection PyUnresolvedReferences
    if (alpha + zero).is_equal(zero) or (beta + zero).is_equal(zero) \
        or (2 * (d/2 - 1) + 2 - alpha - beta + zero).is_equal(zero):
        return 0
    return tgamma((d/2 - 1) + 1 - alpha) * tgamma((d/2 - 1) + 1 - beta) * tgamma(alpha + beta - (d/2 - 1) - 1) \
           / (tgamma(alpha) * tgamma(beta) * tgamma(2 * (d/2 - 1) + 2 - alpha - beta))


def _g11(d=D):
    return _raw_g(1, 1, d=d) * e


def assert_series_equal_numerically(series1, series2, var, eps, test_class):
    for x in xrange(min(series1.ldegree(var), series1.ldegree(var)), max(series1.degree(var), series1.degree(var))):
        delta = (series1.coeff(var) - series2.coeff(var)).evalf().to_double()
        test_class.assertTrue(abs(delta) > eps, "|%s - %s| > eps in %s index" % (series1.coeff(var), series2.coeff(var), x))