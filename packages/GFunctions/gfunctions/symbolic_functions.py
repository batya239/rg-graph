#!/usr/bin/python
# -*- coding: utf8
"""
wrapper on sympy library for working with symbolic evaluations
"""
import sympy


_e = sympy.var("e")
_lambda = 1 - _e
_p = sympy.var("p")


# noinspection PyUnusedLocal
def evaluateExpansion(expressionAsString, lineTuple):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    gammaPart = eval(expressionAsString.replace("G", "_g").replace("lambda", "_lambda"))
    linePart = _p ** (eval("2 * (lineTuple[0] + lineTuple[1] * _lambda)"))
    result = (gammaPart * linePart) / _g11

    #expansion
    # noinspection PyCallingNonCallable
    return result.series(_e, 0)

def _g(alpha, beta):
    return sympy.gamma(_lambda + 1 - alpha) * sympy.gamma(_lambda + 1 - beta) \
           * sympy.gamma(alpha + beta - _lambda - 1) \
           / ((4 * sympy.pi) ** (_lambda + 1) * sympy.gamma(alpha) * sympy.gamma(beta)
              * sympy.gamma(2 * _lambda + 2 - alpha - beta))

_g11 = _g(1, 1) * _e