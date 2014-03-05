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


def cln(number):
    return swiginac.numeric(str(number))

p, e = var("p e")

Z53 = var("Z53")

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

D = swiginac.numeric("4") - swiginac.numeric("2") * e

p2 = p ** 2

pe = p ** e

CLN_ZERO = swiginac.numeric("0")
CLN_ONE = swiginac.numeric("1")
CLN_MINUS_ONE = swiginac.numeric("-1")
CLN_TWO = swiginac.numeric("2")

l = D / CLN_TWO - CLN_ONE

def series(expression, x, x0, n, remove_order=False):
    res = expression.series(x == x0, n)
    return res.convert_to_poly(no_order=True) if remove_order else res


def subs(expression, z, z0):
    return expression.subs(z == z0)


def evaluate(expression_as_str, strong_to_internal_code=False):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-l*2)*G(1, 4-l*3)'
    lineTuple like (4, -4) ~ 4 - 4 * l
    """
    eps_part = eval(to_internal_code(expression_as_str, strong=strong_to_internal_code))
    return eps_part


def safe_integer_numerators(expression_as_str):
    return re.sub('([\.\d]+)/', 'swiginac.numeric(\'\\1\')/', expression_as_str)
    #return re.sub('([\.\d]+)/', '\\1./', expression_as_str)


def safe_integer_numerators_strong(expression_as_str):
    result = re.sub('([\(\+\*-/])([\d]+)([\)\+\*-/])', '\\1swiginac.numeric(\'\\2\')\\3', expression_as_str)
    result = re.sub('([\(\+\*-/])([\d]+)', '\\1swiginac.numeric(\'\\2\')', result)
    result = re.sub('^([\d]+)([\(\+\*-/])', 'swiginac.numeric(\'\\1\')\\2', result)
    return result


def to_internal_code(expression_as_str, strong=False):
    return safe_integer_numerators_strong(expression_as_str) if strong else safe_integer_numerators(expression_as_str)


def pole_part(expr):
    return expr.series(e == 0, 0).convert_to_poly(no_order=True)


#noinspection PyPep8Naming
def G(alpha, beta, d=D):
    if alpha == 1 and beta == 1:
        return (CLN_ONE / e) * _get_raw_g_pole(d=d)
    return _raw_g(alpha, beta, d=d) / (_g11(d=d)) * _get_raw_g_pole(d=d)


#noinspection PyPep8Naming
def G1(alpha, beta, d=D):
    return (G(alpha, beta, d=d) + G(alpha - CLN_ONE, beta, d=d) - G(alpha, beta - CLN_ONE, d=d))/CLN_TWO


#noinspection PyPep8Naming
def G2(alpha, beta, d=D):
    return (G(alpha, beta, d=d) - G(alpha - CLN_ONE, beta, d=d) - G(alpha, beta - CLN_ONE, d=d))/CLN_TWO


_RAW_G_POLE = dict()
_G_11 = dict()


class IsEqualWrapper(object):
    def __init__(self, underlying):
        self.underlying = underlying

    def __hash__(self):
        return hash(self.underlying)

    def __eq__(self, other):
        return self.underlying.is_equal(other.underlying)


def _get_raw_g_pole(d=D):
    wrapper = IsEqualWrapper(d)
    pole = _RAW_G_POLE.get(wrapper)
    if pole is None:
        pole = series(_raw_g(CLN_ONE, CLN_ONE, d=d), e, 0, 0).coeff(e**(-1))
        _RAW_G_POLE[wrapper] = pole
    return pole


def _raw_g(alpha, beta, d=D):
    #noinspection PyUnresolvedReferences
    if (alpha + zero).is_equal(zero) or (beta + zero).is_equal(zero) \
        or (CLN_TWO * (d/CLN_TWO - CLN_ONE) + CLN_TWO - alpha - beta + zero).is_equal(zero):
        return CLN_ZERO
    return tgamma((d/CLN_TWO - CLN_ONE) + CLN_ONE - alpha) * tgamma(d/CLN_TWO - beta) * tgamma(alpha + beta - d/CLN_TWO) \
           / (tgamma(alpha) * tgamma(beta) * tgamma(d - alpha - beta))


def _g11(d=D):
    wrapper = IsEqualWrapper(d)
    g11 = _G_11.get(wrapper, None)
    if g11 is None:
        g11 = _raw_g(CLN_ONE, CLN_ONE, d=d) * e
        _G_11[wrapper] = g11
    return g11


def check_series_equal_numerically(series1, series2, v, eps, test_class=None):
    series1 = series1.expand()
    series2 = series2.expand()
    for x in xrange(min(series1.ldegree(v), series2.ldegree(v)), max(series1.degree(v), series2.degree(v)) + 1):
        a_coeff = (series1.coeff(v ** x) - series2.coeff(v ** x)).evalf()
        if test_class:
            test_class.assertTrue("to_double" in dir(a_coeff) and abs(a_coeff.to_double()) < eps, "|%s - %s| > eps in %s index \nseries1 %s \nseries2 %s" % (series1.coeff(v ** x), series2.coeff(v ** x), x, series1, series2))
        elif "to_double" not in dir(a_coeff) or abs(a_coeff.to_double()) > eps:
            return False
    return True