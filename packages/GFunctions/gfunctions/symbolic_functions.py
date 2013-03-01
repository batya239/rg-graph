#!/usr/bin/python
# -*- coding: utf8
"""
wrapper on sympy library for working with symbolic evaluations
"""
from sympy import pi, gamma, var


_e = var("e")
_lambda = 1 - _e


def evaluate(expressionAsString):
    eval(expressionAsString.replace("G", "_g").replace("lambda", "_lambda"))


def _g(alpha, beta):
    return str(gamma(_lambda + 1 - alpha) * gamma(_lambda + 1 - beta) \
           * gamma(alpha + beta - _lambda - 1) \
           / (4 * pi) ** (_lambda + 1) * gamma(alpha) * gamma(beta) \
           * gamma(2 * _lambda + 2 - alpha - beta))
