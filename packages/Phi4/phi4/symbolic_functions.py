#!/usr/bin/python
# -*- coding: utf8
#
#
# wrapper on sympy library to evaluate G-functions and eps expansions
#
import re
import sympy

e = sympy.var("e")
l = 1 - e
p = sympy.var("p")

D = 4 - 2 * e

p2 = p ** 2

pe = p ** e

zeta = sympy.zeta
polygamma = sympy.polygamma
pi = sympy.pi
gamma = sympy.gamma
EulerGamma = sympy.EulerGamma


# noinspection PyUnusedLocal
def evaluateSeries(expressionAsString, lineTuple, onlyPolePart=False):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-l*2)*G(1, 4-l*3)'
    lineTuple like (4, -4) ~ 4 - 4 * l
    """
    #expansion
    # noinspection PyCallingNonCallable
    evaluated = series(evaluate(expressionAsString, lineTuple), e, 0, 0, removeO=onlyPolePart)
    return evaluated.removeO() if onlyPolePart else evaluated


def series(expr, x, x0, n, removeO=False):
    """
    sympy bugs avoided
    """
    expr_series = expr.series(x, x0, n)
    return expr_series.removeO() if removeO else expr_series
    # expansion = list()
    # for t in expr.lseries(x, x0):
    #     p = t.as_coeff_exponent(x)[1]
    #     if p < n:
    #         expansion.append(t)
    #     else:
    #         break
    # if not removeO:
    #     expansion.append(sympy.O(x**n))
    # return sympy.Add(*expansion)


def evaluateForTests(expressionAsString):
    """
    use this only for tests please
    """
    return eval(toInternalCode(expressionAsString))


# noinspection PyUnusedLocal
def evaluate(expressionAsString, lineTuple=None):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-l*2)*G(1, 4-l*3)'
    lineTuple like (4, -4) ~ 4 - 4 * l
    """
    gammaPart = eval(toInternalCode(expressionAsString))
    if not lineTuple:
        return gammaPart
    linePart = p ** (eval("(-2) * (lineTuple[0] + lineTuple[1] * l)"))
    return gammaPart * linePart


def toInternalCode(expressionAsString):
    return _safeIntegerNumerators(expressionAsString)


def _safeIntegerNumerators(expressionAsString):
    return re.sub('([\.\d]+)/', 'sympy.Number(\\1)/', expressionAsString)


def polePart(expr):
    return series(expr, e, 0, 0, removeO=True)


def G(alpha, beta):
    if alpha == 1 and beta == 1:
        return 1 / e
    return _rawG(alpha, beta) / _g11


def G1(alpha, beta):
    return (G(alpha, beta) + G(alpha - 1, beta) - G(alpha, beta - 1))/2


def G2(alpha, beta):
    return (G(alpha, beta) - G(alpha - 1, beta) - G(alpha, beta - 1))/2


def _rawG(alpha, beta):
    return gamma(l + 1 - alpha) * gamma(l + 1 - beta) * gamma(alpha + beta - l - 1) \
           / ((4 * pi) ** (l + 1) * gamma(alpha) * gamma(beta) * gamma(2 * l + 2 - alpha - beta))


_g11 = _rawG(1, 1) * e