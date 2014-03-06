#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from math import log
from scipy import integrate
import numpy as np
import time
import math
import re
from numpy import pi as Pi
from math import cos, sin


def scipy_integrate(integrand_series, integrations, scalar_products_functions):
    answer = dict()
    print "Start integration: %s\nIntegration: %s\nScalar functions: %s" % (integrand_series, integrations, scalar_products_functions)
    print "ID: %s" % id(integrand_series)
    ms = time.time()
    for degree, integrand in integrand_series.items():
        for sp_function in scalar_products_functions:
            integrand = integrand.subs(sp_function[0] == sp_function[1])
        try:
            answer[degree] = integrate.nquad(construct_integral_lambda(integrand,  integrations), construct_integral_limits(integrations))[0]
        except BaseException as e:
            raise ValueError(e, "Error in %s" % integrand)
    print "Integration done in %s ms" % (time.time() - ms)
    return answer


def construct_integral_lambda(integrand, integrations):
    integrand_str = safe_integers_numerators(integrand.printpython())
    _vars = map(lambda integration: str(integration.var), integrations)
    lambda_str = "lambda %s: %s" % (",".join(_vars), integrand_str)
    return eval(lambda_str)


def construct_integral_limits(integrations):
    return map(lambda i: [eval(i.a.printpython()), eval(i.b.printpython())], integrations)


def safe_integers_numerators(string):
    return re.sub('([\.\d]+)/', '\\1./', string)