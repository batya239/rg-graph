#!/usr/bin/python
# -*- coding: utf8
"""
wrapper on sympy library for working with symbolic evaluations
"""
import sympy


_e = sympy.var("e")
_lambda = 1 - _e
_p = sympy.var("p")


def _getE():
    return _e


# noinspection PyUnusedLocal
def evaluateSeries(expressionAsString, lineTuple, onlyPolePart=False):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    #expansion
    # noinspection PyCallingNonCallable
    if onlyPolePart:
        return evaluate(expressionAsString, lineTuple).series(_e, 0, 0).removeO()
    else:
        return evaluate(expressionAsString, lineTuple).series(_e, 0, 0)


# noinspection PyUnusedLocal
def evaluate(expressionAsString, lineTuple=None):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    gammaPart = eval(expressionAsString.replace("G", "_g").replace("lambda", "_lambda"))
    if not lineTuple:
        return gammaPart
    linePart = _p ** (eval("2 * (lineTuple[0] + lineTuple[1] * _lambda)"))
    return (gammaPart * linePart) / _g11


def toSerializableCode(expressionAsString):
    return expressionAsString.replace("G", "_g").replace("lambda", "_lambda").replace("e", "_e")


def polePart(expr):
    return (expr + sympy.O(1, _e)).series(_e, 0, 0).removeO()


def _g(alpha, beta):
    return sympy.gamma(_lambda + 1 - alpha) * sympy.gamma(_lambda + 1 - beta) \
           * sympy.gamma(alpha + beta - _lambda - 1) \
           / ((4 * sympy.pi) ** (_lambda + 1) * sympy.gamma(alpha) * sympy.gamma(beta)
              * sympy.gamma(2 * _lambda + 2 - alpha - beta))


_g11 = _g(1, 1) * _e