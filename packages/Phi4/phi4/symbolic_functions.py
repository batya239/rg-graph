#!/usr/bin/python
# -*- coding: utf8
"""
wrapper on sympy library for working with symbolic evaluations
"""
import re
import sympy


e = sympy.var("e")
l = 1 - e
p = sympy.var("p")

p2 = p ** 2

pe = p ** e

zeta = sympy.zeta
polygamma = sympy.polygamma
pi = sympy.pi


# noinspection PyUnusedLocal
def evaluateSeries(expressionAsString, lineTuple, onlyPolePart=False):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    #expansion
    # noinspection PyCallingNonCallable
    if onlyPolePart:
        return evaluate(expressionAsString, lineTuple).series(e, 0, 0).collect(e).removeO()
    else:
        return evaluate(expressionAsString, lineTuple).series(e, 0, 0).collect(e)


def evaluateForTests(expressionAsString):
    """
    use this only for tests please
    """
    return eval(toInternalCode(expressionAsString))


# noinspection PyUnusedLocal
def evaluate(expressionAsString, lineTuple=None):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    gammaPart = eval(toInternalCode(expressionAsString))
    if not lineTuple:
        return gammaPart
    linePart = p ** (eval("2 * (lineTuple[0] + lineTuple[1] * l)"))
    return gammaPart * linePart


def toInternalCode(expressionAsString):
    return _safeIntegerNumerators(expressionAsString)


def _safeIntegerNumerators(expressionAsString):
    return re.sub('([\.\d]+)/', 'sympy.Number(\\1)/', expressionAsString)


def polePart(expr, precision=10):
    return (expr + sympy.O(1, e)).collect(e).series(e, 0, 0).removeO()


def G(alpha, beta):
    if alpha == 1 and beta == 1:
        return 1 / e
    return _rawG(alpha, beta) / _g11


def _rawG(alpha, beta):
    return sympy.gamma(l + 1 - alpha) * sympy.gamma(l + 1 - beta) \
           * sympy.gamma(alpha + beta - l - 1) \
           / ((4 * sympy.pi) ** (l + 1) * sympy.gamma(alpha) * sympy.gamma(beta)
              * sympy.gamma(2 * l + 2 - alpha - beta))


_g11 = _rawG(1, 1) * e


