#!/usr/bin/python
# -*- coding: utf8
"""
wrapper on sympy library for working with symbolic evaluations
"""
import re
import sympy


_e = sympy.var("e")
_lambda = 1 - _e
_p = sympy.var("p")

p2 = _p ** 2

pe = _p ** _e


def _getE():
    return _e


def _getP():
    return _p

# noinspection PyUnusedLocal
def evaluateSeries(expressionAsString, lineTuple, onlyPolePart=False):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    #expansion
    # noinspection PyCallingNonCallable
    if onlyPolePart:
        return evaluate(expressionAsString, lineTuple).series(_e, 0, 0).collect(_e).removeO()
    else:
        return evaluate(expressionAsString, lineTuple).series(_e, 0, 0).collect(_e)


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
    linePart = _p ** (eval("2 * (lineTuple[0] + lineTuple[1] * _lambda)"))
    return gammaPart * linePart


def toInternalCode(expressionAsString):
    return _safeIntegerNumerators(expressionAsString.replace("G", "_g") \
        .replace("lambda", "_lambda") \
        .replace("e", "_e") \
        .replace("p", "_p") \
        .replace("_polygamma", "sympy.polygamma") \
        .replace("log", "sympy.log") \
        .replace("z_eta", "sympy.zeta") \
        .replace("_pi", "sympy.pi"))


def _safeIntegerNumerators(expressionAsString):
    return re.sub('(\d+)/', 'sympy.Number(\\1)/', expressionAsString)


def toExternalCode(expressionAsString):
    return expressionAsString \
        .replace("_e", "e") \
        .replace("_p", "p") \
        .replace("_g", "G") \
        .replace("_lambda", "lambda")


def polePart(expr):
    return (expr + sympy.O(1, _e)).collect(_e).series(_e, 0, 0).removeO()


def _g(alpha, beta):
    if alpha == 1 and beta == 1:
        return 1 / _e
    return _rawG(alpha, beta) / _g11


def _rawG(alpha, beta):
    return sympy.gamma(_lambda + 1 - alpha) * sympy.gamma(_lambda + 1 - beta) \
           * sympy.gamma(alpha + beta - _lambda - 1) \
           / ((4 * sympy.pi) ** (_lambda + 1) * sympy.gamma(alpha) * sympy.gamma(beta)
              * sympy.gamma(2 * _lambda + 2 - alpha - beta))


_g11 = _rawG(1, 1) * _e