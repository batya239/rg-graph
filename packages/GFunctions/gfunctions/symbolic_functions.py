#!/usr/bin/python
# -*- coding: utf8
"""
wrapper on sympy library for working with symbolic evaluations
"""
from sympy import pi, gamma, var, series


_e = var("e")
_lambda = 1 - _e
_p = var("p")


# noinspection PyUnusedLocal
def evaluate(expressionAsString, lineTuple):
    """
    expressionAsString like '('G(1, 1)*G(1, 1)*G(1, 3-lambda*2)*G(1, 4-lambda*3)'
    lineTuple like (4, -4) ~ 4 - 4 * lambda
    """
    gammaPart = eval(expressionAsString.replace("G", "_g").replace("lambda", "_lambda"))
    linePart = _p ** (eval("2 * (lineTuple[0] - lineTuple[1] * _lambda)"))
    result = gammaPart * linePart

    #expansion
    # noinspection PyCallingNonCallable
    expansion = series(result, _e, 0)
    print expansion
    print type(expansion)
    assert False


def _g(alpha, beta):
    return gamma(_lambda + 1 - alpha) * gamma(_lambda + 1 - beta) \
           * gamma(alpha + beta - _lambda - 1) \
           / ((4 * pi) ** (_lambda + 1) * gamma(alpha) * gamma(beta)
              * gamma(2 * _lambda + 2 - alpha - beta))